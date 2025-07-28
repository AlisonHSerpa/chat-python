import time
import json
from ..service import WriterService

# session key usa writerService para fazer autosave
class SessionKey:
    def __init__(self, key, username, expiration_seconds=3600, max_messages=100, valid=True):
        self.username = username
        self.key = key
        self.creation_time = time.time()
        self.expiration_seconds = expiration_seconds
        self.remaining_messages = max_messages
        self.valid = valid
        self.save_session()  # Salva imediatamente

    # pode ser usado no __init__ para passar o valor da key
    @staticmethod
    def generate_shared_key(A, B):
        # Exemplo: substitua isso pela lógica real de DH se necessário
        return A + B

    def to_json(self):
        return json.dumps({
            "username": self.username,
            "key": self.key,
            "creation_time": self.creation_time,
            "expiration_seconds": self.expiration_seconds,
            "remaining_messages": self.remaining_messages,
            "valid": self.valid
        }, indent=2)

    def is_expired(self):
        return time.time() > self.creation_time + self.expiration_seconds

    def check_session_key(self):
        if self.is_expired():
            self.valid = False
            self.save_session()
        return self.valid

    def count_limit(self):
        if self.remaining_messages <= 0:
            self.valid = False
        else:
            self.remaining_messages -= 1
        self.save_session()
        return self.valid

    def save_session(self):
        WriterService.write_session(self.to_json(), self.username)
