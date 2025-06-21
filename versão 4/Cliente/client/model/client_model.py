import random
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
from queue import Queue

class ClientModel:
    def __init__(self):
        self.username = self._generate_random_name()
        self.socket = None
        self.message_queue = Queue()
        self.connected = False

    def _generate_random_name(self):
        random_names = [
            "Luffy", "Zoro", "Nami", "Sanji", "Chopper", 
            "Robin", "Franky", "Brook", "Jinbe", "Shanks"
        ]
        return random.choice(random_names)

    def connect_to_server(self, host='127.0.0.1', port=8000):
        try:
            self.socket = socket(AF_INET, SOCK_STREAM)
            self.socket.connect((host, port))
            self.connected = True
            return True
        except Exception as e:
            return str(e)

    def disconnect(self):
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        self.connected = False

    def send_message(self, message):
        if self.connected:
            try:
                self.socket.sendall(message.encode())
                return True
            except Exception as e:
                return str(e)
        return "Not connected"

    def start_listening(self, callback):
        def listen():
            while self.connected:
                try:
                    response = self.socket.recv(1500).decode()
                    if not response:
                        break
                    self.message_queue.put(response)
                except Exception as e:
                    self.message_queue.put(f"Erro: {e}")
                    break
            self.connected = False
            self.message_queue.put("Desconectado do servidor")

        Thread(target=listen, daemon=True).start()