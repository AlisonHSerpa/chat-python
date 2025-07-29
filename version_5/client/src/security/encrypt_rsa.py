from .translate_pem import Translate_Pem
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes

class encrypt_rsa:
    # Este método recebe uma chave pública do destinatário e a usa encriptar dados. É usado no Diffie-Hellman para enviar os 
    # dados que resultam na chave compartilhada. Como a chave é armazenada em formato PEM, ela é convertida para o objeto de chave pública.
    @staticmethod
    def encrypt_with_public_key(pem_peer_public_key, message):

        # A chave pública é carregada a partir do conteúdo PEM.
        peer_public_key = Translate_Pem.receive_key(pem_peer_public_key)
        
        # A mensagem é encriptada com a chave pública do destinatário.
        ciphertext = peer_public_key.encrypt(
            message,
            padding=serialization.OAEP(
                mgf=serialization.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return ciphertext

    # Este método recebe uma chave privada do usuário e a usa para descriptografar dados. É usado no Diffie-Hellman. 
    # A chave privada é recebida em formato PEM e convertida para o objeto de chave privada. 
    @staticmethod
    def decrypt_with_private_key(pem_private_key, ciphertext):
        # A chave privada é carregada a partir do conteúdo PEM.
        private_key = Translate_Pem.receive_private_key(pem_private_key)
        # A mensagem é descriptografada com a chave privada do usuário.
        plaintext = private_key.decrypt(
            ciphertext,
            padding=serialization.OAEP(
                mgf=serialization.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return plaintext