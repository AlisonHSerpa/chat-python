from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from base64 import b64decode
from ..repository import Repository

class Cryptograph:
    @staticmethod
    def verify_signature(username, signed_body, original_challenge):
        # Pega os dados do cliente (chave pública salva em formato PEM)
        data = Repository.get_client_by_username(username)
        pem_public_key = data["key"].encode()

        # Carrega a chave pública
        public_key = serialization.load_pem_public_key(pem_public_key)

        # Decodifica a assinatura recebida (em base64)
        signature = b64decode(signed_body)

        try:
            # Verifica a assinatura digital (se a assinatura bate com o desafio original)
            public_key.verify(
                signature,
                original_challenge if isinstance(original_challenge, bytes) else original_challenge.encode(),
                padding.PKCS1v15(),  # ou PSS se usado no cliente
                hashes.SHA256()
            )
            return True  # assinatura válida
        except Exception as e:
            print("Assinatura inválida:", e)
            return False
