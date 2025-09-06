from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

class Assinatura:
    
    # Esta classe é responsável por assinar digitalmente mensagens usando RSA, ou checar a assinatura de mensagens.
    @staticmethod
    def sign_message(private_key, message):
        '''Assina uma mensagem com a chave privada RSA. 
        O método de assinatura utiliza o padding PSS e o hash SHA256.'''
        signature = private_key.sign(
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return signature

# ------------------------------------------------------------------------

    @staticmethod
    def _encrypt_message_aes_hmac(message: str, aes_key: bytes, hmac_key: bytes) -> bytes:
        import os
        import hmac
        import hashlib
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
        from cryptography.hazmat.backends import default_backend
        from cryptography.hazmat.primitives import padding

        # Gera IV aleatório (16 bytes para AES)
        iv = os.urandom(16)

        # Pad no texto (AES precisa múltiplo de 16)
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(message.encode()) + padder.finalize()

        # Criptografa
        cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()

        # Monta pacote: IV + ciphertext
        data = iv + ciphertext

        # Gera HMAC
        tag = hmac.new(hmac_key, data, hashlib.sha256).digest()

        # Retorna pacote final: IV + CIPHERTEXT + HMAC
        return data + tag

    @staticmethod
    def _decrypt_message_aes_hmac(token: bytes, aes_key: bytes, hmac_key: bytes) -> str: 
        import hmac
        import hashlib
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
        from cryptography.hazmat.backends import default_backend
        from cryptography.hazmat.primitives import padding

        # Divide partes
        iv = token[:16]
        ciphertext = token[16:-32]
        recv_tag = token[-32:]

        # Verifica HMAC
        data = iv + ciphertext
        calc_tag = hmac.new(hmac_key, data, hashlib.sha256).digest()
        if not hmac.compare_digest(calc_tag, recv_tag):
            raise ValueError("HMAC inválido: dados foram adulterados")

        # Descriptografa
        cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        padded_data = decryptor.update(ciphertext) + decryptor.finalize()

        # Remove pad
        unpadder = padding.PKCS7(128).unpadder()
        data = unpadder.update(padded_data) + unpadder.finalize()

        return data.decode('utf-8')
    
    @staticmethod
    def encrypt_and_send_message(plaintext : str, target: str, username : str):
        from ..model import MessageModel
        from ..service import MailService , WriterService
        from ..security import DiffieHelmanHelper as dhh
        import json
        import base64

        session_key = json.loads(WriterService.get_session_key(target))
        aes_key = base64.b64decode(session_key["aes_key"])
        hmac_key = base64.b64decode(session_key["hmac_key"])
        
        ciphertext = Assinatura._encrypt_message_aes_hmac(plaintext, aes_key, hmac_key)
        b64_ciphertext = dhh.b64e(ciphertext)

        '''
            message = {
            "type" : type,
            "from" : origin,
            "to" : destiny,
            "body" : body
        '''

        # Monta a mensagem
        message = MessageModel("message", username, target, b64_ciphertext)

        # Envia a mensagem
        MailService.send_to_mailman(message.get_message())
        message.message["body"] = plaintext
        return message

    @staticmethod
    def receive_and_decrypt_message(message : dict):
        from ..security import DiffieHelmanHelper as dhh
        from ..service import WriterService
        import json
        import base64

        ciphertext = dhh.b64d(message["body"])
    
        session_key = json.loads(WriterService.get_session_key(message["from"]))
        aes_key = base64.b64decode(session_key["aes_key"])
        hmac_key = base64.b64decode(session_key["hmac_key"])

        message["body"] = Assinatura._decrypt_message_aes_hmac(ciphertext, aes_key, hmac_key)
        Assinatura._verify_time_message_session(session_key, message)

        WriterService.save_message(message)

        
    @staticmethod
    def _verify_time_message_session(session_key : dict, message : dict):
        from datetime import datetime
        from ..service import SessionKeyService, WriterService

        dt_session = datetime.now().fromisoformat(session_key["datetime"])
        dt_message = datetime.now().fromisoformat(message["datetime"])

        delta = dt_session - dt_message

        if delta.total_seconds() >= 3600:
            WriterService.delete_session_key(message["origin"])
            SessionKeyService.iniciar_DH(message["origin"])

# ----------------------------------------------------------------
    @staticmethod
    def send_improvised_message(plaintext : str, target: str, username : str):
        from ..model import MessageModel
        from ..service import MailService

        '''
            message = {
            "type" : type,
            "from" : origin,
            "to" : destiny,
            "body" : body
        '''
        ciphertext = Assinatura._encrypt_cesar(7, plaintext)

        # Monta a mensagem
        message = MessageModel("message_improvised", username, target, ciphertext)

        # Envia a mensagem
        MailService.send_to_mailman(message.get_message())
        message.message["body"] = plaintext
        return message

    @staticmethod
    def receive_improvised_message(message : dict):
        from ..service import WriterService

        '''
            message = {
            "type" : type,
            "from" : origin,
            "to" : destiny,
            "body" : body
        '''
        message["body"] = Assinatura._decrypt_cesar(7, message["body"])
        WriterService.save_message(message)

# -------------------------------------------------------
    aphabet_cesar_cipher = (
            "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            "abcdefghijklmnopqrstuvwxyz"
            "0123456789"
            " !@#$%^&*()-_=+[]{};:'\",.<>?/\\|`~"
        )

    @staticmethod
    def _search_alphabet(letra):
        """Retorna o índice da letra no alfabeto, ou None se não estiver."""
        if letra in Assinatura.aphabet_cesar_cipher:
            return Assinatura.aphabet_cesar_cipher.index(letra)
        return None

    @staticmethod
    def _encrypt_cesar(chave, plainText):
        n = len(Assinatura.aphabet_cesar_cipher)
        cipherText = ""

        for letra in plainText:
            gt = Assinatura._search_alphabet(letra)
            if gt is not None:
                cipherText += Assinatura.aphabet_cesar_cipher[(gt + chave) % n]
            else:
                cipherText += letra  # mantém caracteres fora do alfabeto

        return cipherText

    @staticmethod
    def _decrypt_cesar(chave, cipherText):
        n = len(Assinatura.aphabet_cesar_cipher)
        plainText = ""

        for letra in cipherText:
            gt = Assinatura._search_alphabet(letra)
            if gt is not None:
                plainText += Assinatura.aphabet_cesar_cipher[(gt - chave) % n]
            else:
                plainText += letra  # mantém caracteres fora do alfabeto

        return plainText