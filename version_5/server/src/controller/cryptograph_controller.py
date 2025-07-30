from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from base64 import b64decode

class Cryptograph:
    @staticmethod
    def verify_signature(repository, username, signed_body_b64, original_challenge):
        # Busca chave pública do repositório
        data = repository.get_client_by_username(username)
        pem_public_key = data["key"].encode()  # PEM string para bytes

        # Carrega chave pública
        public_key = serialization.load_pem_public_key(pem_public_key)

        # Decodifica a assinatura (que vem como string base64)
        signature = b64decode(signed_body_b64)

        try:
            public_key.verify(
                signature,
                original_challenge,  # já está em bytes
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except Exception as e:
            print("Assinatura inválida:", e)
            return False
