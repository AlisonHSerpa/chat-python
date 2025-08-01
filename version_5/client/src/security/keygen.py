# version_5/client/src/security/keygen.py
from cryptography.hazmat.primitives.asymmetric import dh
from cryptography.hazmat.primitives.asymmetric import rsa
from .translate_pem import Translate_Pem

class Keygen:

    '''# Esta classe é responsável por gerar chaves criptográficas RSA.'''
   
   
    # O código abaixo gera as chave privada e pública PERSISTENTES (RSA) que serão usadas para o diffie-helman posteriormente.
    @staticmethod
    def generate_rsa_keys():
        private_key = rsa.generate_private_key(65537, 2048) # Expoente é um número primo que é usado para o cálculo, 2048 é o tamanho da chave criada
        public_key = private_key.public_key()

        # As chaves são convertida para o formato PEM, que é um formato de texto legível por humanos.
        pem_priv = Translate_Pem.chave_para_pem(private_key)
        
        pem_pub = Translate_Pem.chave_para_pem(public_key)

        # As chaves são retornadas em formato PEM para serem armazenadas em um arquivo PEM. 
        return pem_priv, pem_pub
    