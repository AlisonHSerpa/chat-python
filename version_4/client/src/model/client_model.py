import random
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
from queue import Queue
import json
from ..service import WriterService 
import os
from ..view import ask_username

class ClientModel:
    def __init__(self):
        self.writer = WriterService()
        self.username = None
        self.askName()
        self.socket = None
        self.message_queue = Queue()
        self.connected = False
        self.server_host = None
        self.server_port = None

    def askName(self):
        ''' pergunta o nome do usuario caso nao exista um arquivo usuario'''
        diretorio = "./user.txt"
        if os.path.exists(diretorio):
            self.username = self.writer.read_file(diretorio)
        else:
            self.username = ask_username()  # Chama a janela gráfica
        
            if not self.username:
                print("Nenhum nome foi digitado.")
                return

            try:         
                self.writer.write_file(diretorio, self.username)
            except Exception as e:
                print(f"erro ao criar um usuario: {e}")

    def connect_to_server(self, host='127.0.0.1', port=8000):
        ''' faz a conexao com o servidor '''
        try:
            self.server_host = host
            self.server_port = port
            self.socket = socket(AF_INET, SOCK_STREAM)
            self.socket.connect((host, port))
            
            # Primeira ação ao conectar: enviar o username para o servidor
            self._send_username_to_server(self.username)
            
            self.connected = True
            return True
        except Exception as e:
            return str(e)

    def _send_username_to_server(self, username):
        """Envia o username para o servidor assim que conecta"""
        self.socket.sendall(self.mount_message("changeusername","server", username).encode())

    def disconnect(self):
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        self.connected = False

    def send_message(self, destiny, body):
        ''' envia uma mensagem para o servidor '''
        if self.connected:
            try:
                self.socket.sendall(self.mount_message( "message" ,destiny, body).encode())
                return True
            except Exception as e:
                return str(e)
        return "Not connected"

    def set_username(self, new_username):
        """Atualiza o username localmente e no servidor"""
        self.username = new_username
        if self.connected:
            self._send_username_to_server(new_username)

    def receive_data(self, data):
        ''' decodifica o json'''
        json_data = json.loads(data)
        return json_data
        
    def mount_message(self, type, destiny, body):
        ''' monta um json mensagem '''
        message = {
            "type": type,
            "from": self.username,
            "to" : destiny,
            "body": body
        }

        data = json.dumps(message)
        return data