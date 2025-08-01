import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes, hmac
from cryptography.hazmat.primitives import padding
from ..model import SessionKey


# Esta classe utiliza as chaves síncronas AES e HMAC para encriptar e desencriptar as mensagens gerais.
class Encrypt_DH:

    # Método que recebe a chave e a encripta usando a chave AES obtida através do Diffie Helman
    def encrypt_with_aes(plaintext):

        aes_key = SessionKey.send_aes_key()

        iv = os.urandom(16)  # AES block size

        padder = padding.PKCS7(128).padder()

        padded_data = padder.update(plaintext) + padder.finalize()

        cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv))
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()
        
        return iv, ciphertext
    
    # Método que recebe o conteúdo encriptado pela chave AES e gera um
    def generate_hmac(data: bytes) -> bytes:
        hmac_key = SessionKey.send_hmac_key()
        h = hmac.HMAC(hmac_key, hashes.SHA256())
        h.update(data)
        return h.finalize()
 
    # Método que será chamado para encriptar e assinar o conteúdo pré envio 
    @staticmethod
    def prepare_send_message_dh(plaintext):
        iv, cipher = Encrypt_DH.encrypt_with_aes(plaintext)
        hmac = Encrypt_DH.generate_hmac(iv + cipher)
        return iv + cipher + hmac
    
    # método que descriptografa a mensagem
    def decrypt_aes(iv, ciphertext):
        cipher = Cipher(algorithms.AES(SessionKey.send_aes_key), modes.CBC(iv))
        decryptor = cipher.decryptor()
        padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()

        unpadder = padding.PKCS7(128).unpadder()
        plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()
        return plaintext

    # Método que receberá a mensagem
    @staticmethod
    def recebe_mensagem(dados):
        received_iv = dados[:16]
        received_ciphertext = dados[16:-32]
        received_mac = dados[-32:]

        try:
            h = hmac.HMAC(SessionKey.send_hmac_key, hashes.SHA256())
            h.update(received_iv + received_ciphertext)
            h.verify(received_mac)  # Lança exceção se inválido
            return Encrypt_DH.decrypt_aes(received_iv, received_ciphertext)


        except Exception as e:
            print(f"Erro ao verificar mensagem recebida com chave síncrona: {e}")





