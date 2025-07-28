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

    # O código abaixo lê o arquivo de parâmetros para a geração de chaves
    @staticmethod
    def get_parameters():
        with open("version_5\client\src\security\dh_params.pem", "rb") as f:
            parameters = load_pem_parameters(f.read())
        return parameters

    # O código abaixo gera as chave privada e pública PERSISTENTES que serão usadas para o diffie-helman posteriormente.
    @staticmethod
    def generate_keys():
        private_key = rsa.generate_private_key() # Olhar na documentação o tamanho da chave e etc
        public_key = private_key.public_key()

        pem_priv = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()  # ou com senha
        )
        
        pem_pub = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
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

    # TODO: Ler o arquivo e separar as funções de chave assimétrica do RSA e diferenciar a 
    # função do Diffie_Helman com os segredos.

    # TODO: Servidor irá enviar um número que será encriptado pela chave privada do usuário e 
    # descriptada pela chave pública presente no servidor

    # Obtém ambas as chaves e decodifica em formato string UTF-8 para passar para o 
    # Writer Service armazenar ambas as chaves.
    @staticmethod
    def get_private_key(private_key):
        pem_bytes = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        return pem_bytes.decode('utf-8') # Transforma a chave em bytes.

    @staticmethod
    def get_public_key(private_key):
        pem_bytes = private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return pem_bytes.decode('utf-8') # Transforma a chave em bytes.
    
    # A função abaixo irá fazer o cálculo da chave compartilhada
    @staticmethod
    def create_shared_key(A, B):
        # Faz o exchange entre as chaves privada e pública (do outro cliente) para obter a compartilhada.
        shared_key = A.exchange(B)
        # Deriva a chave compartilhada para ser usada como chave simétrica.
        derived_key = HKDF(
            algorithm=hashes.SHA256(),
            length=64,
            salt=None,
            info=b'handshake data',
        ).derive(shared_key)

        chave_encript = derived_key[:32] # Para o AES-256
        chave_hmac = derived_key[32:] # HMAC-SHA256

        # Como ambas as chaves serão salvas como texto, é necessário decodificá-las para base64.
        encript_b64 = base64.urlsafe_b64encode(chave_encript).decode("utf-8")
        hmac_b64 = base64.urlsafe_b64encode(chave_hmac).decode("utf-8")
        # Para retorná-las ao estado normal, basta refazer o processo ao contrário (trocar encode por decode e vice-versa).

        # Como a chave derivada se divide em duas, a função as retornará como uma tupla.
        return encript_b64, hmac_b64