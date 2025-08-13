import json

class MessageDH:
    def __init__(self, type, origin, target, param, salt, key):
        self.message = {
            "type" : type,
            "from" : origin,
            "to" : target,
            "parametros" : param,
            "salt" : salt,
            "key" : key
        }

    def get_message(self):
        return json.dumps(self.message)
    
    @staticmethod
    def receive_data(response):
        return json.loads(response)