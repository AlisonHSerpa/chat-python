import json

class MessageModel:
    def __init__(self, type, origin, destiny, body):
        self.message = {
            "type" : type,
            "from" : origin,
            "to" : destiny,
            "body" : body
        }

    def get_message(self):
        return json.dumps(self.message)
    
    @staticmethod
    def receive_data(response):
        return json.loads(response)