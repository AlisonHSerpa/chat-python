from ..model import MessageModel
from .mail_service import MailService
from .writer_service import WriterService
import json

class SessionKeyService:

    rsa_public_keys = {}

    @staticmethod
    def request_public_key(user , target):
        ''' envia para o meilman um pedido para enviar a chave publica rsa do target '''
        request = MessageModel("request_key", user, target, "")
        print("mensagem montada")
        MailService.send_to_mailman(request.get_message())
        print("mensagem enviada")
        print(request.get_message())

    @staticmethod
    def verificar_session_key(target):
        '''
        Verifica se há uma session key salva para o usuário target.
        Retorna False se não houver ou se ocorrer erro ao ler.
        '''
        try:
            session = WriterService.get_session_key(target)
            return session is not None and session.get("valid", False)
        except (FileNotFoundError, json.JSONDecodeError, ValueError, RuntimeError) as e:
            print(f"[verificar_session_key] Erro ao verificar sessão de '{target}': {e}")
            return False


    @staticmethod
    def verificar_rsa_pub_key(target):
        ''' verifica se tem rsa_pub_key, se não tiver, pede e retorna falso'''
        # procura do dicionario o target para devolver sua rsa_pub_key
        if target in SessionKeyService.rsa_public_keys:
            return SessionKeyService.rsa_public_keys[target]
        else:
            return False

   
    @staticmethod
    def insert_rsa_public_key(target, rsa_pub_key):
        ''' Recebe e salva rsa_pub_key e começar o DH em SessionController '''
        SessionKeyService.rsa_public_keys[target] = rsa_pub_key
        # já aproveita pra começar o DH em SessionController