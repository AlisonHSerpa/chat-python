from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

class Assinatura:

    aphabet_cesar_cipher = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 "
    
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

    @staticmethod
    def decrypt_cesar (chave, cipherText):
        n = len(Assinatura.aphabet_cesar_cipher)
        plainText = ""

        for i in range(len(cipherText)):
            letra = cipherText[i]
            gt = Assinatura.search_alphabet(letra, Assinatura.aphabet_cesar_cipher)
            plainText += Assinatura.aphabet_cesar_cipher[(gt - chave) % n]

        print("texto descriptografado com a chave " + str(chave) + " : " + plainText)

    @staticmethod
    def encrypt_cesar (chave, plainText):
        n = len(Assinatura.aphabet_cesar_cipher)
        cipherText = ""

        for i in range(len(plainText)):
            letra = plainText[i]
            gt = Assinatura.search_alphabet(letra, Assinatura.aphabet_cesar_cipher)
            cipherText += Assinatura.aphabet_cesar_cipher[(gt + chave) % n]

        print("texto criptografado com a chave " + str(chave) + " : " + cipherText)
    
    @staticmethod 
    def search_alphabet(letra):
        for i in range(len(Assinatura.aphabet_cesar_cipher)):
            if Assinatura.aphabet_cesar_cipher[i] == letra:
                return i

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

        WriterService.save_message(message)