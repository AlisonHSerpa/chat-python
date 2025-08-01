import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes, hmac
from cryptography.hazmat.primitives import padding
from ..model import SessionKey


# Esta classe utiliza as chaves síncronas AES e HMAC para encriptar as mensagens gerais.
class Encrypt_DH:

    # Método que recebe a chave e a encripta usando a chave AES obtida através do Diffie Helman
    def encrypt_with_aes(plaintext):
        # TODO: Função que chama a classe Session Key, que contém a chave AES.
        aes_key = SessionKey.send_aes_key()

        iv = os.urandom(16)  # AES block size

        padder = padding.PKCS7(128).padder()

        padded_data = padder.update(plaintext) + padder.finalize()

        cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv))
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()
        
        return iv, ciphertext
    
    # Método que recebe o conteúdo encriptado pela chave AES e gera um
    def generate_hmac(hmac_key: bytes, data: bytes) -> bytes:
        h = hmac.HMAC(hmac_key, hashes.SHA256())
        h.update(data)
        return h.finalize()
 
