# ARQUIVO DE TESTE

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import dh
from cryptography.hazmat.primitives.serialization import load_pem_parameters

from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from cryptography.fernet import Fernet
import base64

def get_parameters():
    with open("version_5\client\src\security\dh_params.pem", "rb") as f:
        parameters = load_pem_parameters(f.read())
    return parameters

minha_chave_privada = get_parameters().generate_private_key()

chave_publica_do_outro = get_parameters().generate_private_key().public_key()

# 1. Gerar chave compartilhada via Diffie-Hellman
shared_key = minha_chave_privada.exchange(chave_publica_do_outro)

# 2. Derivar uma chave de 32 bytes
derived_key = HKDF(
    algorithm=hashes.SHA256(),
    length=32,
    salt=None,              # ou um salt conhecido, se quiser reproduzibilidade
    info=b'fernet-key'
).derive(shared_key)

# 3. Codificar para o formato aceito pelo Fernet
fernet_key = base64.urlsafe_b64encode(derived_key)

# 4. Criar instância do Fernet
f = Fernet(fernet_key)

# 5. Usar para criptografar/decriptar
mensagem = b"mensagem secreta"
criptografado = f.encrypt(mensagem)
decriptografado = f.decrypt(criptografado)

print(f'Mensagem criptografada {criptografado.decode('utf-8')}')
print(f'Mensagem descriptografada {decriptografado.decode('utf-8')}')
