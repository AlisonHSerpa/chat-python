import json
import os
import base64

from cryptography.hazmat.primitives.asymmetric import rsa, padding, dh
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.backends import default_backend

class DiffieHelmanHelper:
    # =========================================================
    # Utilitários de (de)serialização
    # =========================================================
    @staticmethod
    def b64e(b: bytes) -> str:
        return base64.b64encode(b).decode("utf-8")

    @staticmethod
    def b64d(s: str) -> bytes:
        return base64.b64decode(s.encode("utf-8"))

    # =========================================================
    # RSA helpers
    # =========================================================

    @staticmethod
    def rsa_generate():
        priv = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        pub = priv.public_key()
        return priv, pub

    @staticmethod
    def rsa_encrypt(pubkey, data: bytes) -> bytes:
        return pubkey.encrypt(
            data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )

    @staticmethod
    def rsa_decrypt(privkey, data: bytes) -> bytes:
        return privkey.decrypt(
            data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )

    # =========================================================
    # AES-GCM (transporte)
    # =========================================================
    @staticmethod
    def aesgcm_encrypt(key: bytes, plaintext: bytes, aad: bytes = None):
        """
        Retorna (nonce, ciphertext_with_tag). AESGCM.encrypt já embute o tag no final.
        """
        if aad is None:
            aad = b""
        aesgcm = AESGCM(key)
        nonce = os.urandom(12)  # 96-bit nonce recomendado para GCM
        ct = aesgcm.encrypt(nonce, plaintext, aad)
        return nonce, ct

    @staticmethod
    def aesgcm_decrypt(key: bytes, nonce: bytes, ciphertext_with_tag: bytes, aad: bytes = None) -> bytes:
        if aad is None:
            aad = b""
        aesgcm = AESGCM(key)
        return aesgcm.decrypt(nonce, ciphertext_with_tag, aad)

    # =========================================================
    # "Envelope" híbrido: cifra payload com AES-GCM e chave AES com RSA
    # =========================================================
    @staticmethod
    def encrypt_for(recipient_rsa_pub, clear_payload_bytes: bytes, aad: bytes = None) -> dict:
        aes_key = os.urandom(32)  # 256-bit
        nonce, ct = DiffieHelmanHelper.aesgcm_encrypt(aes_key, clear_payload_bytes, aad=aad)
        enc_key = DiffieHelmanHelper.rsa_encrypt(recipient_rsa_pub, aes_key)
        return {
            "k": DiffieHelmanHelper.b64e(enc_key),   # AES key cifrada com RSA
            "n": DiffieHelmanHelper.b64e(nonce),     # nonce do AES-GCM
            "c": DiffieHelmanHelper.b64e(ct),        # ciphertext+tag AES-GCM
            # "aad": opcional se quiser mandar metadado/versão
        }
    
    @staticmethod
    def decrypt_from(own_rsa_priv, envelope: dict, aad: bytes = None) -> bytes:
        enc_key = DiffieHelmanHelper.b64d(envelope["k"])
        nonce = DiffieHelmanHelper.b64d(envelope["n"])
        ct = DiffieHelmanHelper.b64d(envelope["c"])
        aes_key = DiffieHelmanHelper.rsa_decrypt(own_rsa_priv, enc_key)
        return DiffieHelmanHelper.aesgcm_decrypt(aes_key, nonce, ct, aad=aad)

    # =========================================================
    # Diffie-Hellman (efêmero) + HKDF
    # =========================================================
    # Parâmetros DH globais (p, g). Gerados uma vez no servidor (ou fixos no sistema).
    DH_PARAMETERS = dh.generate_parameters(generator=2, key_size=2048)

    @staticmethod
    def dh_generate():
        priv = DiffieHelmanHelper.DH_PARAMETERS.generate_private_key()
        pub = priv.public_key()
        return priv, pub

    @staticmethod
    def dh_pub_serialize_pem(pub) -> bytes:
        return pub.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )

    @staticmethod
    def dh_pub_load_pem(pem_bytes: bytes):
        return serialization.load_pem_public_key(pem_bytes, backend=default_backend())

    @staticmethod
    def dh_priv_serialize_pem(priv) -> bytes:
        return priv.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )

    @staticmethod
    def dh_priv_load_pem(pem_bytes: bytes):
        return serialization.load_pem_private_key(pem_bytes, password=None, backend=default_backend())

    @staticmethod
    def dh_derive_shared_secret(priv_key, peer_pub_key) -> bytes:
        return priv_key.exchange(peer_pub_key)

    @staticmethod
    def hkdf_derive(shared_secret: bytes, salt: bytes, info: bytes = b"chat-session"):
        """
        64 bytes de saída -> 32 p/ AES, 32 p/ HMAC
        """
        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=64,
            salt=salt,
            info=info,
            backend=default_backend(),
        )
        okm = hkdf.derive(shared_secret)
        return okm[:32], okm[32:]  # (aes_256_key, hmac_256_key)

    # =========================================================
    # Método completo para estabelecimento de sessão DH
    # =========================================================
    @staticmethod
    def establish_dh_session(priv_key, peer_pub_key, salt: bytes = None, info: bytes = b"chat-session"):
        if salt is None:
            salt = os.urandom(16)  # Salt aleatório se não fornecido
            
        shared_secret = DiffieHelmanHelper.dh_derive_shared_secret(priv_key, peer_pub_key)
        aes_key, hmac_key = DiffieHelmanHelper.hkdf_derive(shared_secret, salt, info)
        return {
            'aes_key': aes_key,
            'hmac_key': hmac_key,
            'salt': salt
        }