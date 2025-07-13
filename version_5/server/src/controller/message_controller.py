from ..model import *
from socket import socket, AF_INET, SOCK_STREAM

class MessageController:
    def __init__(self, server):
        self.server = server

    def sendMessage(self, socket, message):
        socket.sendAll(message.encode())
        return None

    def retrieve_old_messages(self, key):
        client = ClientModel.get_client_by_key(key)
        path = f"<path>/{client.username}"

        return None