class MessageModel:
    def __init__(self, type, origin, destiny, body):
        self.message = {
            "type": type,
            "from": origin,
            "to": destiny,
            "body": body
        }

    def get_message(self):
        return self.message
    
    ''' escrever a mensgem na lista de nao enviadas'''
    def hold_message(self):
        return None
    
    ''' ler mensagem da lista de nao enviadas '''
    @staticmethod
    def recover_message(username):
        path = f"<path>/{username}"
        return None