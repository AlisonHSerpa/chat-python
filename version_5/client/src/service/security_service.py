# TODO: Criar uma classe que contém funções designadas para a segurança dos dados armazenados e enviados. A classe obviamente precisa de uma cifra pessoal específica para armazenar as informações e outra para enviar e receber mensagens. Importa-se uma biblioteca chamada 'cryptography' para aplicar as funções da criptografia. 


from cryptography.fernet import Fernet

# Função generate_keys() é responsãvel por criar uma chave local, que será usada para encriptar quaisquer dados usados pela função writer service (que é responável por armazenar dados locais), e as chaves privada e pública, que serão usadas para fazer o handshake entre 2 clientes. 
# Note que todas as chaves são guardadas como bytes, por outra função que chama o generate_keys().

@staticmethod
def generate_keys(): 
    local_key = Fernet.generate_key().decode() # Chave local, usada para acesso de dados locais.
    
    private_key = Fernet.generate_key().decode() # Chave privada, conhecida apenas pelo usuário. Pode descriptar mensagens encriptadas pela chave pública, ou encriptar mensagens que só podem ser desencriptadas pela chave pública. 
    
    public_key = Fernet.generate_key().decode() # Chave pública, inversa da privada. Pode ser acessada por qualquer cliente, e é inserida no banco de dados.

    return local_key, private_key, public_key

# Função encrypt_message receberá uma mensagem em 
@staticmethod
def encrypt_message(): 
    data = message
    fernet = Fernet(key) 