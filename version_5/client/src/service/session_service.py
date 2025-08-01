from ..model import MessageModel
from .mail_service import MailService
from ..controller import SessionController

class SessionKeyService:

    rsa_public_keys = {}

    @staticmethod
    def request_public_key(user , target):
        request = MessageModel("request_key", user, target, "")
        print("mensagem montada")
        MailService.send_to_mailman(request.get_message())
        print("mensagem enviada")
        print(request.get_message())


    ''' 2 
        verifica se tem session
            se não tiver retorna falso
        
         
         verifica se tem rsa_pub_key
            se não tiver, pede e retorna falso
    '''

    ''' 3
        Recebe e salva rsa_pub_key

        já aproveita pra começar o DH em SessionController
    '''