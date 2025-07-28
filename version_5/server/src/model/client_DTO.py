class ClienteDTO:
    def __init__(self, username, key):
        self.username = username
        self.key = key
    
    def make_json(self):
        data = {
            "username": self.username,
            "key": self.key
        }

        return data