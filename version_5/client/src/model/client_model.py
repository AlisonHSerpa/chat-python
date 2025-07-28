from socket import socket, AF_INET, SOCK_STREAM
from queue import Queue
from ..service import WriterService 
import os
from ..view import ask_username
from .message_model import MessageModel
from ..security import Keygen
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from base64 import b64encode, b64decode

class ClientModel:
    def __init__(self):
        self.message_queue = Queue()
        self.connected = False
        self.connect_to_server()        # server ip pode ser uma env.example

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
            self.private_key = data["private_key"]
            self.public_key = data["public_key"]
            self.local_key = data["local_key"]

            # faz login
            self.login()

        else:
            self.username = ask_username()  # Chama a janela gráfica
        
            if not self.username:
                print("Nenhum nome foi digitado.")
                return

            try:
                # As chaves são criadas a partir do método com RSA
                self.private_key, self.public_key = Keygen.generate_keys()

                # escreve um user.txt
                WriterService.write_client(self.jsonify())

                # cadastra no servidor
                self.sign_up()
            except Exception as e:
                print(f"erro ao criar um usuario: {e}")


    def connect_to_server(self, host='127.0.0.1', port=8000):
        ''' faz a conexao com o servidor '''
        try:
            self.server_host = host
            self.server_port = port
            self.socket = socket(AF_INET, SOCK_STREAM)
            self.socket.connect((host, port))
            
            # Primeira ação ao conectar: dizer quem eh para o servidor
            self.start_client()
            
            self.connected = True
        except Exception as e:
            print(e)
            return str(e)

    def login(self):
        try:
            if not self.socket:
                raise ConnectionError("Socket não está conectado.")

            # 1. Envia solicitação de login
            hello = MessageModel("login", self.username, "server", "Hello server!")
            self.socket.sendall(hello.get_message().encode())

            # 2. Recebe o desafio (test)
            response = self.socket.recv(1024).decode()
            json_data = MessageModel.receive_data(response)
            challenge = json_data["body"]

            # 3. Converte chave privada de string PEM para objeto
            private_key = serialization.load_pem_private_key(
                self.private_key.encode(),  # sua chave deve estar em string PEM
                password=None
            )

            # 4. Cria assinatura digital do desafio
            signature = private_key.sign(
                challenge.encode() if isinstance(challenge, str) else challenge,
                padding.PKCS1v15(),
                hashes.SHA256()
            )

            # 5. Envia resposta assinada (em base64)
            encoded_signature = b64encode(signature).decode()
            answer = MessageModel("login", self.username, "server", encoded_signature)
            self.socket.sendall(answer.get_message().encode())

            # 6. Recebe permissão final do servidor
            response = self.socket.recv(1024).decode()
            permission = MessageModel.receive_data(response)

            if permission["type"] == "erro":
                raise ConnectionError("Servidor reprovou o teste da chave.")

            print("Login bem-sucedido!")

        except Exception as e:
            print(f"Erro no login: {e}")
            self.disconnect()


    def sign_up(self):
        try:
            message = MessageModel("sign up", self.username, "server", self.public_key)
            self.socket.sendall(message.get_message().encode())

            response = self.socket.recv(1024).decode()
            message = MessageModel.receive_data(response)

            if message["type"] == "erro":
                raise ConnectionError("Erro no cadastro do servidor.")

        except Exception as e:
            print(f"Erro no login: {e}")
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

    def send_message(self, message):
        ''' envia uma mensagem para o servidor '''
        if self.connected:
            try:
                self.socket.sendall(message.get_message().encode())
                return True
            except Exception as e:
                return str(e)
        return "Not connected"
    
    def jsonify(self):
        data = {
            "username" : self.username,
            "private_key": self.private_key,
            "public_key": self.public_key,
            "local_key": self.local_key
        }
        return data