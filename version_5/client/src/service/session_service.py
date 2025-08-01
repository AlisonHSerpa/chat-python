from ..model import MessageModel
from .mail_service import MailService

class SessionKeyService:

    @staticmethod
    def request_public_key(user , target):
        request = MessageModel("request_key", user, target, "")
        print("mensagem montada")
        MailService.send_to_mailman(request.get_message())
        print("mensagem enviada")
        print(request.get_message())