import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes, hmac
from cryptography.hazmat.primitives import padding
import base64
from  ..service import WriterService


# Esta classe utiliza as chaves síncronas AES e HMAC para encriptar e desencriptar as mensagens gerais.

# ela recebe String e Byte e devolve string e byte
class Encrypt_DH:

    # Método que recebe a chave e a encripta usando a chave AES obtida através do Diffie Helman
    def encrypt_with_aes(plaintext : str, bit_aes_key : bytes):

        iv = os.urandom(16)  # AES block size

        padder = padding.PKCS7(128).padder()

        padded_data = padder.update(plaintext) + padder.finalize()

        cipher = Cipher(algorithms.AES(bit_aes_key), modes.CBC(iv))
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()
        
        return iv, ciphertext
    
    # Método que recebe o conteúdo encriptado pela chave AES e gera um
    def generate_hmac(data: bytes, hmac_key) -> bytes:
        h = hmac.HMAC(hmac_key, hashes.SHA256())
        h.update(data)
        return h.finalize()
 
    # Método que será chamado para encriptar e assinar o conteúdo pré envio 
    @staticmethod
    def prepare_send_message_dh(plaintext : str, aes_key : bytes, hmac_key : bytes) -> bytes:
        iv, cipher = Encrypt_DH.encrypt_with_aes(plaintext, aes_key)
        hmac = Encrypt_DH.generate_hmac(iv + cipher, hmac_key)
        return iv + cipher + hmac
    
    # método que descriptografa a mensagem
    def decrypt_aes(iv : bytes, ciphertext : bytes, aes_key : bytes):
        cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv))
        decryptor = cipher.decryptor()
        padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()

        unpadder = padding.PKCS7(128).unpadder()
        plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()
        return plaintext

    # Método que receberá a mensagem
    @staticmethod
    def recebe_ciphertext(ciphertext, target):
        dados = base64.b64decode(ciphertext.encode('utf-8'))

        received_iv = dados[:16]
        received_ciphertext = dados[16:-32]
        received_mac = dados[-32:]
        
        # acha a chave de sessao
        session_key = WriterService.get_session_key(target)
        aes_key = base64.b64decode(session_key["aes_key"].encode('utf-8'))
        hmac_key = base64.b64decode(session_key["hmac_key"].encode('utf-8'))

        try:
            h = hmac.HMAC(hmac_key, hashes.SHA256())
            h.update(received_iv + received_ciphertext)
            h.verify(received_mac)  # Lança exceção se inválido
            return Encrypt_DH.decrypt_aes(received_iv, received_ciphertext, aes_key)


        except Exception as e:
            print(f"Erro ao verificar mensagem recebida com chave síncrona: {e}")





