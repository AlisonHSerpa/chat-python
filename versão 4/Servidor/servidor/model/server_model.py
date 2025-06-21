from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
import sys

class ServerModel:
    def __init__(self):
        self.server_socket = socket(AF_INET, SOCK_STREAM)
        self.clientes = []
        self.socket_to_username = {}
    
    def initialize_server(self, host='0.0.0.0', port=8000):
        """Inicializa o socket do servidor"""
        self.server_socket.bind((host, port))
        self.server_socket.listen()
        print(f'Aguardando por novas conexões na porta {port}')
    
    def add_client(self, client_socket, client_address):
        """Adiciona um novo cliente à lista"""
        self.clientes.append(client_socket)
        print(f'Nova conexão de: {client_address}')
    
    def remove_client(self, client_socket, client_address):
        """Remove um cliente da lista"""
        if client_socket in self.clientes:
            self.clientes.remove(client_socket)
            username = self.socket_to_username.pop(client_address, None)
            if username:
                print(f"{username} saiu do chat.")
                return username
        return None
    
    def map_username(self, client_address, username):
        """Mapeia um nome de usuário ao endereço do cliente"""
        self.socket_to_username[client_address] = str(username)
    
    def get_username(self, client_address):
        """Obtém o nome de usuário associado a um endereço"""
        return self.socket_to_username.get(client_address)
    
    def get_online_users(self):
        """Retorna lista de usuários online"""
        return [name for name in self.socket_to_username.values()]
    
    def get_recipient_socket(self, target_username):
        """Encontra o socket do destinatário pelo nome de usuário"""
        for socket in self.clientes:
            try:
                socket_address = socket.getpeername()
                if socket_address in self.socket_to_username:
                    if self.socket_to_username[socket_address].lower() == target_username.lower():
                        return socket
            except:
                continue
        return None
    
    def close_all(self):
        """Fecha todas as conexões"""
        for cliente in self.clientes[:]:
            cliente.close()
        self.server_socket.close()