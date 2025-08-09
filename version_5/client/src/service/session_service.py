from ..model import MessageModel
from .mail_service import MailService
from .writer_service import WriterService
import json
import time

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
            return session is not None
        except (FileNotFoundError, json.JSONDecodeError, ValueError, RuntimeError) as e:
            print(f"[verificar_session_key] Erro ao verificar sessão de '{target}': {e}")
            return False


    @staticmethod
    def verificar_rsa_pub_key(username, target, interval=0.5, timeout=None):
        """
        Verifica e aguarda até obter a chave pública RSA do target.
        Envia o request apenas uma vez. Espera até receber a chave.
        """
        # Se já estiver disponível, retorna imediatamente
        if target in SessionKeyService.rsa_public_keys:
            return SessionKeyService.rsa_public_keys[target]

        # Envia o request uma única vez
        print(f"[verificar_rsa_pub_key] Solicitando chave pública de {target}...")
        SessionKeyService.request_public_key(username, target)

        # Começa a espera
        start_time = time.time()
        while True:
            if target in SessionKeyService.rsa_public_keys:
                print(f"[verificar_rsa_pub_key] Chave de {target} recebida.")
                return SessionKeyService.rsa_public_keys[target]

            if timeout is not None and (time.time() - start_time > timeout):
                raise TimeoutError(f"Timeout esperando chave pública de {target}")

            time.sleep(interval)


    @staticmethod
    def iniciar_DH(target):
        from ..controller import SessionController2
        SessionController2.diffie_hellman_1(target, SessionKeyService.rsa_public_keys[target])

    @staticmethod
    def insert_rsa_public_key(target, rsa_pub_key):
        ''' Recebe e salva rsa_pub_key e começar o DH em SessionController '''
        SessionKeyService.rsa_public_keys[target] = rsa_pub_key
        # já aproveita pra começar o DH em SessionController