import base64

class HalfKey:
    def __init__(self, target, salt, dh_private_key):
        self.salt = salt
        self.target = target
        self.dh_private_key = dh_private_key
        self.save_half_key()

    def jsonify(self):
        return {
            "usuario_alvo" : self.target,
            "dh_private_key" : base64.b64encode(self.dh_private_key),
            "salt" : base64.b64encode(self.salt)
        }
    
    def save_half_key(self):
        from ..service import WriterService
        WriterService.insert_half_key

    @staticmethod
    def get_data_in_bytes(data):
        dh_private_key = base64.decode(data["dh_private_key"])
        salt = base64.decode(data["salt"])

        return dh_private_key, salt