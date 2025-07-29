# version_5/client/src/security/keygen.py
from cryptography.hazmat.primitives.asymmetric import dh
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import load_pem_parameters
from .translate_pem import Translate_Pem

class Keygen:

    # Esta classe é responsável por gerar e manipular chaves criptográficas,
    # incluindo chaves RSA e Diffie-Hellman.
   
   
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
    
   
    # O código abaixo lê o arquivo de parâmetros para a geração de chaves.
    # Os parãmetros são usados para o Diffie-Hellman, que é um protocolo de troca de chaves.
    # O arquivo de parâmetros deve ser gerado previamente e armazenado no diretório especificado.
    # Os parâmetros são sempre 2 e 2048, mas eles sempre serão gerados por quem iniciou a sessão.
    @staticmethod
    def get_parameters():
        with open("version_5/client/src/security/dh_params.pem", "rb") as f:
            parameters = load_pem_parameters(f.read())
        return parameters
    
    # O código abaixo gera uma chave privada e pública temporária para o Diffie-Hellman.
    # A chave privada é gerada a partir dos parâmetros lidos do arquivo e 
    # a chave pública é gerada a partir da chave privada. 
    # A chave privada é inserida na função Diffie-Helman e a pública é enviada para o destinatário via socket.
    @staticmethod
    def generate_temporary_keys():
        parameters = Translate_Pem.get_parameters() # lê os parâmetros do arquivo de quem começou a sessão
        private_key = dh.generate_private_key(parameters) # Gera a chave privada temporária
        public_key = private_key.public_key() # Gera a chave pública temporária

        return private_key, public_key
    