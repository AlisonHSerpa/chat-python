from socket import socket, AF_INET, SOCK_STREAM
from queue import Queue
from ..service import WriterService 
import os
from ..view import ask_username
from .message_model import MessageModel
from ..security.keygen import Keygen
from ..security.translate_pem import Translate_Pem
from ..security.sign_message import Assinatura
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from base64 import b64encode, b64decode
from ..controller import MailController

class ClientModel:
    def __init__(self):
        self.connected = False
        self.start_client()

    def start_client(self):
        ''' pergunta o nome do usuario caso nao exista um arquivo usuario'''
        dir = WriterService.get_user_file_path()
        folder = os.path.dirname(dir)

        # garante que a pasta exista (se quiser garantir)
        if not os.path.exists(folder):
            os.makedirs(folder)

        # verifica se o arquivo existe
        if os.path.exists(dir):
            data = WriterService.read_client()

            # retira os dados que ja existem
            self.username = data["username"]
            self.private_key = data["private_key"].encode('utf-8')  # Aqui a chave é re-codificada para bytes
            # no momento que entra para as variáveis locais.
            self.public_key = data["public_key"].encode('utf-8')  # Aqui a chave é re-codificada para bytes.
            self.local_key = data["local_key"]

            # faz login
            self.login()

        else:
            # As chaves são criadas a partir do método com RSA
            self.private_key, self.public_key = Keygen.generate_keys()
            self.local_key = 2

            # cadastra no servidor
            self.sign_up()

    ''' Método para login no servidor
    O login é feito através de uma assinatura digital do desafio enviado pelo servidor.
    O desafio é assinado com a chave privada do usuário e a assinatura é enviada de volta ao servidor.
    Se o servidor aceitar a assinatura, o login é bem-sucedido.
    Caso contrário, o login falha e o usuário é desconectado.'''
    def login(self):
        try:
            if not self.socket:
                raise ConnectionError("Socket não está conectado.")

            # 1. Envia solicitação de login com MessageModel
            hello = MessageModel("login", self.username, "server", "Hello server!")
            print(hello.get_message())
            MailController.socket.sendall(hello.get_message().encode())

            # 2. Recebe o desafio do servidor    
            challenge_b64 = MailController.socket.recv(1500).decode()
            challenge = b64decode(challenge_b64)  # 3. Decodifica o desafio

            # 4. Carrega chave privada
            private_key = Translate_Pem.receive_key(self.private_key)
            print(private_key)

            # 5. Assina o desafio com a chave privada
            signature = Assinatura.sign_message(private_key, challenge)

            # 6. Codifica e envia a assinatura de volta ao servidor
            print("Enviando assinatura ao servidor...")
            signature_b64 = b64encode(signature).decode()  # Transforma em string base64
            MailController.socket.sendall(signature_b64.encode())  # Envia como string

            # 7. Recebe a resposta do servidor
            print("Aguardando resposta do servidor...")
            result = MailController.socket.recv(1500).decode()
            if result == "OK":
                print("Login aceito!")
            else:
                raise ConnectionError("Login recusado pelo servidor.")

        except Exception as e:
            print(f"Erro no login: {e}")
            self.disconnect()


    def sign_up(self, string = None):
        try:
            self.username = ask_username(string)  # Chama a janela gráfica
        
            if not self.username:
                print("username eh null")
                self.disconnect()
                return

            # Se a chave for bytes, decodifique para string
            pubkey_str = self.public_key
            
            message = MessageModel("sign up", self.username, "server", pubkey_str)
            MailController.socket.sendall(message.get_message().encode())

            response = MailController.socket.recv(1024).decode()
            message = MessageModel.receive_data(response)

            if message["type"] == "erro":
                self.sign_up(message["body"])
            elif message["type"] == "autorized":
                # escreve um user.txt
                WriterService.write_client(self.jsonify())

        except Exception as e:
            print(f"Erro no cadastro: {e}")
            self.disconnect()  

    def disconnect(self):
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
                print("disconect pass")
            self.socket = None
        self.connected = False
    
    def jsonify(self):
        data = {
            "username": self.username,
            "private_key": self.private_key,
            "public_key": self.public_key,
            "local_key": self.local_key
        }
        return data