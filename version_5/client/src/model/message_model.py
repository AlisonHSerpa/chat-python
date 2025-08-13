import json
from datetime import datetime

class MessageModel:
    def __init__(self, type, origin, destiny, body, key = None, aes = None, iv = None, public_key = None):
        now = datetime.now()
        self.message = {
            "type" : type,
            "from" : origin,
            "to" : destiny,
            "body" : body,
            "key" : key,
            "aes" : aes,
            "iv" : iv,
            "public_key" : public_key,
            "date" : now.date().isoformat(),
            "time" : now.strftime("%H:%M")
        }

    def get_message(self):
        return json.dumps(self.message)
    
    @staticmethod
    def receive_data(response):
        return json.loads(response)
    