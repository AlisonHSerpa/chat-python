from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

class Assinatura:
    
    # Esta classe é responsável por assinar digitalmente mensagens usando RSA, ou checar a assinatura de mensagens.
    @staticmethod
    def sign_message(private_key, message):
        '''Assina uma mensagem com a chave privada RSA. 
        O método de assinatura utiliza o padding PSS e o hash SHA256.'''
        signature = private_key.sign(
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return signature
