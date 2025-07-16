from socket import socket, AF_INET, SOCK_STREAM
from ..repository import *

class ClientModel:
    def  __init__(self, username, socket, address, key):
        self.socket = socket
        self.username = username
        self.address = address
        self.key = key # chave publica do usuario
    
    ''' metodos para mudar o nome do usuario'''
    def getUsername(self):
        return self.username

    def setUsername(self, username):
        self.username = username

    ''' metodos para registrar o usuario'''
    def register_new_client(self, repository):
        if not repository.get_client_by_key(self.key):
            data = {
                "username": self.username,
                "key": self.key
            }
            repository.insert_client(data)

    ''' metodos para chamar o leitor (buscas)'''
    @staticmethod
    def get_client_by_username(repository, username):
        repository.find_client_by_username(username)

    @staticmethod
    def get_client_by_key(repository, key):
        repository.find_client_by_key(key)
    