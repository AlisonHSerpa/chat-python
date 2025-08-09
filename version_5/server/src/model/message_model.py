import json
from datetime import datetime

class MessageModel:
    def __init__(self, type, origin, destiny, body, key = None, param = None, aes = None, iv = None):
        now = datetime.now()
        self.message = {
            "type" : type,
            "from" : origin,
            "to" : destiny,
            "body" : body,
            "key" : key,
            "param" : param,
            "aes" : aes,
            "iv" : iv ,
            "date" : now.date().isoformat(),
            "time" : now.strftime("%H:%M")
        }

    def get_message(self):
        return json.dumps(self.message)
    
    def get_message_as_dict(self):
        return self.message
    
    ''' escrever a mensgem na lista de nao enviadas'''
    def hold_message(self,repository):
        repository.insert_message(self.get_message_as_dict())
    
    ''' ler mensagem da lista de nao enviadas '''
    @staticmethod
    def recover_message_from_client(repository, username):
        repository.find_client_by_username(username)

    @staticmethod
    def receive_data(response):
        return json.loads(response)