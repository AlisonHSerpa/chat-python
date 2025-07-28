# Este arquivo serve para armazenar as funções de criação de senhas que serão implementadas na criação de perfis.

# Os imports abaixo trazem as funções de derivação de chave, diffie-helman e parãmetros.

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.asymmetric import dh
from cryptography.hazmat.primitives.serialization import load_pem_parameters
import base64

# O código abaixo lê o arquivo de parâmetros para a geração de chaves
def get_parameters():
    with open("version_5\client\src\security\dh_params.pem", "rb") as f:
        parameters = load_pem_parameters(f.read())
    return parameters

# O código abaixo gera as chave privada e pública PERSISTENTES que serão usadas para o diffie-helman posteriormente.
def generate_keys():
    private_key = get_parameters().generate_private_key()
    return private_key

# Obtém ambas as chaves e decodifica em formato string UTF-8 para passar para o Writer Service armazenar ambas as chaves.
def get_private_key(private_key):
    pem_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    return pem_bytes.decode('utf-8') # Transforma a chave em bytes.

def get_public_key(private_key):
    pem_bytes = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    return pem_bytes.decode('utf-8') # Transforma a chave em bytes.

# A função abaixo irá fazer o cálculo da chave compartilhada
def create_shared_key(private_key, peer_public_key):
    # Faz o exchange entre as chaves privada e pública (do outro cliente) para obter a compartilhada.
    shared_key = private_key.exchange(peer_public_key)
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