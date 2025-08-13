from datetime import datetime
import json
from ..service import WriterService
import base64
from datetime import datetime

# session key usa writerService para fazer autosave
class SessionKey:
    def __init__(self, target, aes: bytes, hmac: bytes):
        self.target = target
        self.aes = base64.b64encode(aes).decode("utf-8")
        self.hmac = base64.b64encode(hmac).decode("utf-8")
        self.save_session_key()

    def to_json(self):
        return json.dumps({
            "target" : self.target,
            "aes_key": self.aes,
            "hmac_key": self.hmac,
            "creation_time": datetime.now().strftime("%H:%M"),
        })

    def save_session_key(self):
        from ..service import WriterService
        WriterService.insert_session_key(self.to_json(), self.target)
        print("session key feita")
