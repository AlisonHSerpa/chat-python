from datetime import datetime
import json
from ..service import WriterService
from ..security.diffie_helman import Diffie_Helman
from ..security.translate_pem import Translate_Pem

# session key usa writerService para fazer autosave
class SessionKey:
    def __init__(self, username, rsa_peer_public_key, peer_username, expiration_seconds=3600, max_messages=100, valid=True):
        self.username = username
        self.rsa_peer_public_key = rsa_peer_public_key
        self.peer_username = peer_username  # Nome do destinatário, para indicar o usuário com quem a sessão é estabelecida

        self.aes_key, self.hmac_key = None  # Chaves para criptografia e verificação de integridade
        self.salt = None # 
        self.dh_private_key = None  # Chave privada temporária

        self.creation_time = datetime.now().strftime("%H:%M")
        self.expiration_seconds = expiration_seconds
        self.remaining_messages = max_messages
        self.valid = valid
        self.save_session()  # Salva imediatamente

    @staticmethod
    def set_session_key(salt, parameters: bytes, peer_public_key: bytes):

        if parameters is None and salt is None:
            print("Parâmetros e salt não fornecidos, " \
            "então a chave privada já foi gerada e o salt já está presente nas variáveis locais.")

            salt = SessionKey.get_salt()  # Pega o salt da variável local.

            private_key = SessionKey.get_dh_private_key()  # Pega a chave privada da variável local.
            
            # Gera a chave de sessão usando a chave privada temporária e a chave pública do destinatário.
            aes_key, hmac_key = Diffie_Helman.diffie_Helman(private_key, peer_public_key, salt)

            # Define as chaves AES e HMAC após o Diffie Helman ser usado.
            set_keys(aes_key, hmac_key)  # Define as chaves AES e HMAC após o Diffie Helman ser usado.
            
            SessionKey.set_salt(None)  # Define o salt como None, pois já foi definido anteriormente.
            
            SessionKey.set_dh_private_key(None)  # Define a chave privada como None após ser usada.
            
            save_session()  # Salva a sessão com as novas chaves.
            
            print("Chave de sessão gerada com sucesso.")

            return None # Como não há necessidade de enviar nada novamente, o retorno é nulo.



        elif parameters is not None and salt is not None:
            # Gera a chave de sessão usando os parâmetros e o salt fornecidos
            private_key, public_key = Diffie_Helman.generate_temporary_keys(parameters)

            pem_public_key = Translate_Pem.chave_para_pem(public_key)
                
            # Gera a chave de sessão usando a chave privada temporária e a chave pública do destinatário.
            aes_key, hmac_key = Diffie_Helman.diffie_Helman(private_key, peer_public_key, salt)

            # Define as chaves AES e HMAC após o Diffie Helman ser usado.
            SessionKey.set_keys(aes_key, hmac_key)
            SessionKey.set_salt(None)  # Define o salt como None, pois já foi definido anteriormente.
            SessionKey.set_dh_private_key(None)  # Define a chave privada como None após ser usada.
            SessionKey.save_session()  # Salva a sessão com as novas chaves.
            print("Chave de sessão gerada com sucesso.")

            return pem_public_key

        else:
            print("Informações incompletas, não é possível gerar a chave de sessão.")
            return None  # Retorna None se não for possível gerar a chave de sessão.
    
    # Define as chaves AES e HMAC após o Diffie Helman ser usado.
    def set_keys(self, aes_key: bytes, hmac_key: bytes):
        self.aes_key = aes_key
        self.hmac_key = hmac_key
        self.save_session()

    # Define e retorna a chave privada diffie_helman momentânea
    def get_dh_private_key(self):
        return self.dh_private_key
    
    def set_dh_private_key(self, dh_private_key):
        self.dh_private_key = dh_private_key


    # Retorna a chave AES 
    def get_aes_key(self):
        return self.aes_key

    # Envia para a função de encriptação
    @staticmethod
    def send_aes_key():
        return SessionKey.get_aes_key()

    # Retorna o salt.
    def get_salt(self):
        return self.salt
    
    def set_salt(self, salt):
        self.salt = salt
        self.save_session()

    def to_json(self):
        return json.dumps({
            "username": self.username,
            "peer_username": self.peer_username,
            "aes_key": self.aes_key.decode('utf-8'),  # Chave AES em formato string
            "hmac_key": self.hmac_key.decode('utf-8'),  # Chave HMAC em formato string
            "creation_time": self.creation_time,
            "expiration_seconds": self.expiration_seconds,
            "remaining_messages": self.remaining_messages,
            "valid": self.valid
        }, indent=2)

    def is_expired(self):
        return datetime.now().strftime("%H:%M") > self.creation_time + self.expiration_seconds

    def check_session_key(self):
        if self.is_expired():
            self.valid = False
            self.save_session()
        return self.valid

    def count_limit(self):
        if self.remaining_messages <= 0:
            self.valid = False
        else:
            self.remaining_messages -= 1
        self.save_session()
        return self.valid

    def save_session(self):
        WriterService.write_session_key(self.to_json(), self.username)
