from socket import socket, AF_INET, SOCK_STREAM

class ClientModel:
    def  __init__(self, socket, username):
        self.socket = socket
        self.username = username
    
    def getUsername(self):
        return self.username

    def setUsername(self, username):
        self.username = username