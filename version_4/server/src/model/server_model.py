from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
import sys
import time
from .client_model import ClientModel
import json

class ServerModel:
    def __init__(self):
        self.server_socket = socket(AF_INET, SOCK_STREAM)
        self.clients = []  # Lista de objetos ClientModel
    
    def initialize_server(self, host='0.0.0.0', port=8000):
        """Inicializa o socket do servidor"""
        self.server_socket.bind((host, port))
        self.server_socket.listen()
        print(f'Aguardando por novas conexões na porta {port}')
    
    def check_connections(self):
        while True:
            for client in self.clients[:]:
                try:
                    client.socket.sendall(b'PING')
                    # Esperar por PONG dentro do timeout
                except:
                    self.remove_client(client.socket)
            time.sleep(60)  # Verificar a cada minuto

    def add_client(self, client_socket, client_address, username = None):
        """Adiciona um novo cliente à lista"""
        client = ClientModel(client_socket, client_address, username)
        self.clients.append(client)
        print(f'Nova conexão de: {client_address}')
        return client
    
    def remove_client(self, client_socket):
        """Remove um cliente da lista"""
        for client in self.clients[:]:
            if client.socket == client_socket:
                self.clients.remove(client)
                print(f"{client.username} saiu do chat.")
                return client
        return None
    
    def get_client_by_socket(self, client_socket):
        """Obtém um cliente pelo socket"""
        for client in self.clients:
            if client.socket == client_socket:
                return client
        return None
    
    def get_client_by_username(self, username):
        """Obtém um cliente pelo nome de usuário"""
        for client in self.clients:
            if client.username.lower() == username.lower():
                return client
        return None
    
    def get_online_users(self):
        """Retorna lista de usuários online"""
        return [client.username for client in self.clients]
    
    def get_recipient_socket(self, target_username):
        """Encontra o socket do destinatário pelo nome de usuário"""
        client = self.get_client_by_username(target_username)
        return client.socket if client else None
    
    def close_all(self):
        """Fecha todas as conexões"""
        for client in self.clients[:]:
            client.socket.close()
        self.server_socket.close()

    def receive_data_server(self, data):
        '''decodifica json '''
        json_data = json.loads(data.decode())
        return json_data