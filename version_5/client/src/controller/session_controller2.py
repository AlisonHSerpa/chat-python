from ..security import DiffieHelmanHelper as dhh
from ..security import Translate_Pem
from ..model import HalfKey
from ..model import SessionKey
import base64
import json
import os
from ..service import *
from datetime import datetime

class SessionController2:
    
    @staticmethod
    def diffie_hellman_1(target: str, rsa_public_key_target):
        """Inicia o handshake DH, enviando a primeira mensagem"""
        try:
            user = WriterService.read_client()
            origin = user["username"]
            public_key = user["public_key"]
            B_rsa_pub = Translate_Pem.pem_to_chave(rsa_public_key_target)
            
            # Gera par de chaves DH e salt
            A_dh_priv, A_dh_pub = dhh.dh_generate()
            salt = os.urandom(16)
            
            # Prepara payload
            payload = {
                "type": "DH_1",
                "dh_pub_pem": dhh.dh_pub_serialize_pem(A_dh_pub).decode("utf-8"),
                "salt_b64": dhh.b64e(salt)
            }
            clear_bytes = json.dumps(payload).encode("utf-8")
            
            # Criptografa com RSA do destinatário
            envelope = dhh.encrypt_for(B_rsa_pub, clear_bytes, aad=b"DH_1")
            
            # Salva metade da chave para uso posterior
            half_key = HalfKey(target, salt, A_dh_priv)
            
            # Prepara mensagem no formato MessageModel
            data = {
                "type": "DH_1",
                "from": origin,
                "to": target,
                "body": envelope["c"],  # ciphertext
                "key": envelope["k"],     # chave AES cifrada
                "aes": "",               # não usado aqui
                "iv": envelope["n"],     # nonce
                "public_key": public_key,
            }
            
            print("DH 1 enviado")
            MailService.send_to_mailman(json.dumps(data))
            
        except Exception as e:
            print(f"Erro no DH1: {str(e)}")
            raise

    @staticmethod
    def diffie_hellman_2(response):
        """Responde ao handshake DH, enviando a segunda mensagem"""
        try:
            user = WriterService.read_client()
            origin = user["username"]
            B_rsa_priv = Translate_Pem.pem_to_chave(user["private_key"])
            
            # Decifra o envelope
            envelope = {
                "k": response["key"],
                "n": response["iv"],
                "c": response["body"]
            }
            clear_bytes = dhh.decrypt_from(B_rsa_priv, envelope, aad=b"DH_1")
            payload = json.loads(clear_bytes.decode("utf-8"))
            
            assert payload["type"] == "DH_1"
            A_dh_pub = dhh.dh_pub_load_pem(payload["dh_pub_pem"].encode("utf-8"))
            salt = dhh.b64d(payload["salt_b64"])
            
            # Gera par de chaves DH
            B_dh_priv, B_dh_pub = dhh.dh_generate()
            
            # Deriva chaves de sessão
            shared_secret = B_dh_priv.exchange(A_dh_pub)
            aes_key, hmac_key = dhh.hkdf_derive(shared_secret, salt, b"chat-session")
            
            # Prepara payload de resposta
            payload_resp = {
                "type": "DH_2",
                "dh_pub_pem": dhh.dh_pub_serialize_pem(B_dh_pub).decode("utf-8")
            }
            clear_bytes_resp = json.dumps(payload_resp).encode("utf-8")
            
            # Criptografa com RSA do remetente original
            target_rsa_pub = Translate_Pem.pem_to_chave(response["public_key"])
            envelope_resp = dhh.encrypt_for(target_rsa_pub, clear_bytes_resp, aad=b"DH_2")
            
            # Prepara mensagem de resposta
            data = {
                "type": "DH_2",
                "from": origin,
                "to": response["from"],
                "body": envelope_resp["c"],
                "key": envelope_resp["k"],
                "aes": dhh.b64e(aes_key),
                "iv": envelope_resp["n"],
                "public_key": user["public_key"]
            }
            
            # Salva chaves de sessão localmente
            session_key = SessionKey(response["from"], aes_key, hmac_key)
            
            print("DH 2 enviado")
            MailService.send_to_mailman(json.dumps(data))
            
        except Exception as e:
            print(f"Erro no DH2: {str(e)}")
            raise

    @staticmethod
    def diffie_hellman_3(response):
        """Finaliza o handshake DH usando a half key armazenada"""
        try:
            user = WriterService.read_client()
            origin = user["username"]
            A_rsa_priv = Translate_Pem.pem_to_chave(user["private_key"])
            
            # Decifra o envelope
            envelope = {
                "k": response["key"],
                "n": response["iv"],
                "c": response["body"]
            }
            clear_bytes = dhh.decrypt_from(A_rsa_priv, envelope, aad=b"DH_2")
            payload = json.loads(clear_bytes.decode("utf-8"))
            
            assert payload["type"] == "DH_2"
            B_dh_pub = dhh.dh_pub_load_pem(payload["dh_pub_pem"].encode("utf-8"))
            
            # Recupera half key como string JSON e desserializa
            half_key_json = WriterService.get_half_key(response["from"])
            if half_key_json is None:
                raise ValueError(f"Half key não encontrada para o usuário {response['from']}")
            half_key = json.loads(half_key_json)

            # DECODIFICA base64 antes de passar para pem_to_chave
            dh_priv_key_bytes = base64.b64decode(half_key["dh_private_key"])
            dh_private_key = Translate_Pem.pem_to_chave(dh_priv_key_bytes)

            salt_b64 = half_key["salt"]
            salt = base64.b64decode(salt_b64)

            # Deriva chaves de sessão
            shared_secret = dh_private_key.exchange(B_dh_pub)
            aes_key, hmac_key = dhh.hkdf_derive(shared_secret, salt, b"chat-session")
            
            # Salva chaves de sessão
            session_key = SessionKey(response["from"], aes_key, hmac_key)          
            print(f"Session key estabelecida com {response['from']}")
            
        except Exception as e:
            print(f"Erro no DH3: {str(e)}")
            raise
