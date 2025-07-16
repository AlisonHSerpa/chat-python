from threading import Thread
import sys
import json
import time
from ..model import *
from ..repository import *
from .message_controller import MessageController

class ServerController:
    def __init__(self):
        self.model = ServerModel()
        self.repository = Repository()
        self.message_controller = MessageController(self, self.model)

    def handle_new_connection(self, client_socket, client_address):
        """Processa a conexão inicial do cliente"""
        try:
            # Recebe o handshake de username
            data = client_socket.recv(1500).decode()
            mensagem = json.loads(data)
        
            # verifica se existe
            try:
                data = ClientModel.get_client_by_key(self.repository, mensagem["body"])
                # no futuro tera um teste para ver se a chave privada do cliente esta correta
                # por enquanto vamos assumir que se encontrou esta correto

                client = ClientModel(data["username"],client_socket,client_address,data["key"])
            except:
                # se nao existe, cria
                try:
                    # cria e adiciona no banco de dados
                    client = ClientModel(mensagem["from"], client_socket, client_address, mensagem["body"])
                    client.register_new_client(self.repository)
                except Exception as e:
                    print(f"erro ao salvar novo cliente: {e}")
            finally:
                # adiciona na lista de online
                self.model.clients.append(client)    
                return client
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
            users = [client.username for client in self.model.clients]
            message = MessageModel("userlist","server","all", users)
            for client in list(self.model.clients):
                try:
                    client.socket.sendall(message.get_message().encode())
                except Exception:
                    self.model.clients.remove(client)
            time.sleep(5)
