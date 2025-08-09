import base64
from cryptography.hazmat.primitives import serialization
import json

class HalfKey:
    def __init__(self, target, salt, dh_private_key):
        self.salt = salt
        self.target = target
        self.dh_private_key = dh_private_key
        self.save_half_key()

    def jsonify(self):
        # Serializa a chave privada para bytes PEM primeiro
        pem_key = self.dh_private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        return {
            "usuario_alvo": self.target,
            "dh_private_key": base64.b64encode(pem_key).decode('utf-8'),
            "salt": base64.b64encode(self.salt).decode('utf-8')
        }
    
    def save_half_key(self):
        from ..service import WriterService
        # Passa o JSON string como primeiro parâmetro
        json_data = json.dumps(self.jsonify())
        WriterService.insert_half_key(json_data, self.target)

    @staticmethod
    def get_data_in_bytes(data):
        """Converte os dados base64 de volta para bytes"""
        try:
            pem_key = base64.b64decode(data["dh_private_key"])
            salt = base64.b64decode(data["salt"])
            
            # Desserializa a chave privada
            private_key = serialization.load_pem_private_key(
                pem_key,
                password=None
            )
            
            return private_key, salt
        except Exception as e:
            raise ValueError(f"Erro ao decodificar half key: {str(e)}")