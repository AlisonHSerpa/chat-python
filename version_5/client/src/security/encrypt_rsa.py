from .translate_pem import Translate_Pem
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

class EncryptionRSA:
    # Este método recebe uma chave pública do destinatário e a usa encriptar dados. É usado no Diffie-Hellman 
    # para enviar os dados que resultam na chave compartilhada. Como a chave é 
    # armazenada em formato PEM, ela é convertida para o objeto de chave pública.
    @staticmethod
    def encrypt_with_public_key(message, pem_peer_public_key):
        print("chegou em encrypt_with_public_key(pem_peer_public_key, message)")
        print(message)
        print(pem_peer_public_key)
        # A chave pública é carregada a partir do conteúdo PEM.
        peer_public_key = Translate_Pem.receive_key(pem_peer_public_key)

        print("passou do translate_pem.receive_key")
        print(peer_public_key)
        
        # A mensagem é encriptada com a chave pública do destinatário.
        ciphertext = peer_public_key.encrypt(
            message,
            padding=padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        print(ciphertext)
        print("conseguiu encriptar")
        return ciphertext

    # Este método recebe uma chave privada do usuário e a usa para descriptografar dados. É usado no Diffie-Hellman. 
    # A chave privada é recebida em formato PEM e convertida para o objeto de chave privada. 
    @staticmethod
    def decrypt_with_private_key(ciphertext):
        from ..service import WriterService

        # A chave privada é extraída do json e
        # re-codificada para bytes.
        dados_cliente = WriterService.read_client()
        pem_private_key = dados_cliente["private_key"].encode('utf-8') 

        # A chave privada é carregada a partir do conteúdo PEM.
        private_key = Translate_Pem.receive_key(pem_private_key)

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