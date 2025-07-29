# Este arquivo serve para armazenar as funções de criação de senhas que serão implementadas na criação de perfis.

# Os imports abaixo trazem as funções de derivação de chave, diffie-helman e parãmetros.

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.asymmetric import dh
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import load_pem_parameters
import base64

class Keygen:



    # O código abaixo gera as chave privada e pública PERSISTENTES que serão usadas para o diffie-helman posteriormente.
    @staticmethod
    def generate_keys():
        private_key = rsa.generate_private_key(65537, 2048) # Expoente é um número primo que é usado para o cálculo, 2048 é o tamanho da chave criada
        public_key = private_key.public_key()

        pem_priv = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()  
        )
        
        pem_pub = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        # As chaves são retornadas em formato PEM, que em torno é armazenado em um formato PEM. 
        return pem_priv, pem_pub

    # O código abaixo recebe o conteúdo PEM (que já foi lido e inserido como binário em uma variável)
    # e transforma de volta para uma chave privada.
    @staticmethod
    def receive_private_key(pem_private_key):
        private_key = serialization.load_pem_private_key(
            pem_private_key,
            password=None
        )
        return private_key

    # Mesma coisa que a função acima, só que com a chave pública.
    @staticmethod
    def receive_public_key(pem_public_key):
        public_key = serialization.load_pem_public_key(pem_public_key)
        return public_key
   
   
   
   
   
   
   
    # O código abaixo lê o arquivo de parâmetros para a geração de chaves
    @staticmethod
    def get_parameters():
        with open("version_5/client/src/security/dh_params.pem", "rb") as f:
            parameters = load_pem_parameters(f.read())
        return parameters
    # Os parâmetros fazem parte do cálculo do Diffie-Hellman, que é usado para gerar chaves compartilhadas entre dois usuários.

   
   
   
   
   
   
   
    # Este método recebe uma chave pública do destinatário e a usa encriptar dados. É usado no Diffie-Hellman para enviar os dados que resultam na chave compartilhada. 
    # VOU ASSUMIR QUE no servidor a chave será armazenada em binário, então ele só recebe o conteúdo da chave pública e a usa diretamente, sem precisar de conversão.
    @staticmethod
    def encrypt_with_public_key(peer_public_key, message):
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
    # Neste caso, a chave privada é recebida em formato PEM e convertida para o objeto de chave privada. 
    @staticmethod
    def decrypt_with_private_key(pem_private_key, ciphertext):
        # A chave privada é carregada a partir do conteúdo PEM.
        private_key = Keygen.receive_private_key(pem_private_key)
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
   