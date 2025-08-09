from .translate_pem import Translate_Pem
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

class EncryptionRSA:
    # Este método recebe uma chave pública do destinatário e a usa encriptar dados. É usado no Diffie-Hellman 
    @staticmethod
    def encrypt_with_public_key(data, public_key) -> bytes:
        # Aqui assume que public_key já é um objeto RSAPublicKey, sem passar por pem_to_chave
        encrypted = public_key.encrypt(
            data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return encrypted

    # Este método recebe uma chave privada do usuário e a usa para descriptografar dados. É usado no Diffie-Hellman. 
    # A chave privada é recebida em formato PEM e convertida para o objeto de chave privada. 
    @staticmethod
    def decrypt_with_private_key(ciphertext, private_key):

        # A mensagem é descriptografada com a chave privada do usuário.
        plaintext = private_key.decrypt(
            ciphertext,
            padding=padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return plaintext