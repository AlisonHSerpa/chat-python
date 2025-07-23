import random
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
from queue import Queue
import json
from ..service import WriterService 
import os
from ..view import ask_username
from .message_model import MessageModel

class ClientModel:
    def __init__(self):
        self.writer = WriterService()
        self.message_queue = Queue()
        self.connected = False
        self.connect_to_server()        # server ip pode ser uma env.example

    def start_client(self):
        ''' pergunta o nome do usuario caso nao exista um arquivo usuario'''
        diretorio = "./user.txt"

        # se ouver um cliente salvo nos arquivos
        if os.path.exists(diretorio):
            data = self.writer.read_json(diretorio)

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
                '''
                Aqui deve-se gerar o seguinte json:

                "username" : "",
                "private_key": "",
                "public_key": "",
                "local_key": "",

                '''
                # chaves de teste
                self.public_key = 456
                self.private_key = 123
                self.local_key = 789

                # escreve um user.txt
                self.writer.write_client(diretorio, self.jsonify())

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
            
            test = "Hello server!"
            cript_test = test
            message = MessageModel("login", self.username ,"server", cript_test)
            self.socket.sendall(message.get_message().encode())

            response = self.socket.recv(1024).decode()
            message = MessageModel.receive_data(response)

            if message["type"] == "erro":
                raise ConnectionError("Erro na identificacao do servidor.")

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

    def send_message(self, target, body):
        ''' envia uma mensagem para o servidor '''
        if self.connected:
            try:
                message = MessageModel("message" ,self.username, target, body)
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