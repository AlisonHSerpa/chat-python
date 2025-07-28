from threading import Thread
import sys
import json
import time
from ..model import *
from ..repository import *
from .message_controller import MessageController
from socket import socket, AF_INET, SOCK_STREAM

class ServerController:
    def __init__(self):
        self.model = ServerModel()
        self.repository = Repository()
        self.message_controller = MessageController(self, self.model, self.repository)

    def handle_new_connection(self, client_socket, client_address):
        """Processa a conexão inicial do cliente"""
        try:
            # Recebe o handshake de username
            data = client_socket.recv(1500).decode()
            mensagem = json.loads(data)

            cliente = None  # inicializa para evitar UnboundLocalError

            if mensagem["type"] == "login":
                dict = self.repository.get_client_by_username(mensagem["from"])
                if not dict:
                    response = MessageModel("erro", "server", mensagem["from"], "usuario nao existe")
                    client_socket.sendall(response.get_message().encode())
                    client_socket.close()
                    return None

                if mensagem["body"] == "Hello server!":
                    response = MessageModel("autorized", "server", mensagem["from"], "")
                    client_socket.sendall(response.get_message().encode())

                    # Cria o modelo do cliente conectado
                    cliente = ClientModel(dict["username"], client_socket, client_address, dict["key"])

                    # verificar se ele tem mensagens pendentes
                    self.message_controller.retreive_old_messages(cliente)
                else:
                    response = MessageModel("erro", "server", mensagem["from"], "falha na autenticacao")
                    client_socket.sendall(response.get_message().encode())
                    client_socket.close()
                    return None

            elif mensagem["type"] == "sign up":
                dto = ClienteDTO(mensagem["from"], mensagem["body"])
                self.repository.insert_client(dto.make_json())

                response = MessageModel("autorized", "server", mensagem["from"], "")
                client_socket.sendall(response.get_message().encode())

                cliente = ClientModel(mensagem["from"], client_socket, client_address, mensagem["body"])

            else:
                client_socket.close()
                return None

            self.model.clients.append(cliente)
            return cliente

        except Exception as e:
            print(f"Erro ao configurar novo cliente: {e}")
            client_socket.close()
            return None

    
    def connection_request_loop(self):
        """Aceita novas conexões de clientes"""
        try:
            while True:
                # aceita um novo socket e address
                client_socket, client_address = self.model.server_socket.accept()
                # transforma em cliente
                client = self.handle_new_connection(client_socket, client_address)
                if client:
                    # cria um thread listen para escutar somente ele
                    Thread(target=self.message_controller.listen, args=(client_socket,)).start()
        except KeyboardInterrupt:
            print("\nDesligando servidor...")
            self.model.close_all()

    def list_online_users(self):
        while True:
            users = self.repository.get_all_clients()
            for client in list(self.model.clients):
                try:
                    message = MessageModel("userlist","server",client.username, users)
                    client.socket.sendall(message.get_message().encode())
                except Exception:
                    self.model.clients.remove(client)
            time.sleep(5)
