# TODO: Criar uma classe controlador que funciona como 'porteiro', intervem na transmissão e armazenamento de mensagens. A classe obviamente precisa de uma cifra pessoal específica para armazenar as informações e outra para enviar e receber mensagens. Importa-se uma biblioteca chamada 'cryptography' para aplicar as funções da criptografia. 


from cryptography.fernet import Fernet

# Função abaixo é responsãvel por criar uma chave local, que será usada para encriptar quaisquer dados usados pela função writer service, que é responável por armazenar dados locais. 
def generate_local_key(user): 
    with open("", "wb"):