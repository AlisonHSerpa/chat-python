from socket import socket, AF_INET, SOCK_STREAM
from ..repository import *

class ClientModel:
    def  __init__(self, socket, address, username):
        self.socket = socket
        self.username = username
        self.address = address
        self.online = True
    
    ''' metodos para mudar o nome do usuario'''
    def getUsername(self):
        return self.username

    def setUsername(self, username):
        self.username = username

    def changeOnlineStatus(self, status):
        self.online = status

    ''' metodos para chamar o escritor'''
    def register_new_client(self):
        return None

    ''' metodos para chamar o leitor (buscas)'''
    @staticmethod
    def get_client_by_key():
        return None
    