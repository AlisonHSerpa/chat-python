from threading import Thread
import sys
import json
import time
from ..model import *
from ..repository import *
from .message_controller import MessageController
from socket import socket, AF_INET, SOCK_STREAM
import os
import base64
from .cryptograph_controller import Cryptograph
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization, hashes

class ServerController:
    def __init__(self):
        self.model = ServerModel()
        self.repository = Repository()
        self.message_controller = MessageController(self, self.model, self.repository)

    def handle_new_connection(self, client_socket, client_address):
        """Processa a conexão inicial do cliente"""
        while True:
            try:
                # Recebe o handshake de username
                data = client_socket.recv(1500).decode()

                if not data.strip():  # string vazia ou só espaços
                    break
                mensagem = json.loads(data)

                cliente = None  # inicializa para evitar UnboundLocalError

                if mensagem["type"] == "login":
                    cliente = self.login_client(mensagem, client_socket, client_address)
                    if cliente:
                        self.model.clients.append(cliente)
                        return cliente   # login feito, sai do loop

                elif mensagem["type"] == "sign up":
                    resultado = self.sign_up_client(mensagem, client_socket, client_address)
                    if isinstance(resultado, ClientModel):
                        self.model.clients.append(resultado)
                        return cliente  # cadastro feito com sucesso, sai do loop
                    # senão, apenas espera nova mensagem

                else:
                    break  # tipo desconhecido

            except Exception as e:
                print(f"Erro ao configurar novo cliente: {e}")
                break

        client_socket.close()
        return None

    def login_client(self, mensagem, client_socket, client_address):
        print(f"{client_address} chegou a tentar fazer login")

        dict = self.repository.get_client_by_username(mensagem["from"])
        if not dict:
            response = MessageModel("erro", "server", mensagem["from"], "usuario nao existe")
            client_socket.sendall(response.get_message().encode())
            client_socket.close()
            return None

        if mensagem["body"] == "Hello server!":
            challenge = os.urandom(16)
            client_socket.sendall(base64.b64encode(challenge))  # envia desafio codificado

            signature_b64_bytes = client_socket.recv(4096)  # buffer maior
            signature_b64_str = signature_b64_bytes.decode()  # garante que seja string
            print("Recebeu assinatura do cliente.")

            try:
                if Cryptograph.verify_signature(self.repository, mensagem["from"], signature_b64_str, challenge):
                    client_socket.sendall(b"OK")
                    print(f"Usuário {mensagem['from']} autenticado!")

                    cliente = ClientModel(mensagem["from"], client_socket, client_address, mensagem["body"])
                    return cliente
                else:
                    client_socket.sendall(b"FAIL")
                    print(f"Usuário {mensagem['from']} falhou autenticação.")
            except Exception as e:
                client_socket.sendall(b"FAIL")
                print(f"Erro na verificação de assinatura do usuário {mensagem['from']}: {e}")

        else:
            response = MessageModel("erro", "server", mensagem["from"], "falha na autenticacao")
            client_socket.sendall(response.get_message().encode())
            client_socket.close()
            return None

    def sign_up_client(self, mensagem, client_socket, client_address):
        print(f"{client_address} chegou a tentar fazer cadastro")
        if not self.repository.get_client_by_username(mensagem["from"]) == None :
            response = MessageModel("erro","server",mensagem["from"],"username já existe")
            client_socket.sendall(response.get_message().encode())
            return False

        dto = ClienteDTO(mensagem["from"], mensagem["body"])
        client_data = dto.make_json()  # agora retorna dicionário
        self.repository.insert_client(client_data)

        response = MessageModel("autorized", "server", mensagem["from"], "")
        client_socket.sendall(response.get_message().encode())

        cliente = ClientModel(mensagem["from"], client_socket, client_address, mensagem["body"])
        return cliente

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
            time.sleep(1.5)

    def recv_until_newline(sock):
        buffer = b''
        while True:
            chunk = sock.recv(1024)
            if not chunk:
                break  # conexão fechada
            buffer += chunk
            if b'\n' in buffer:
                line, _, remainder = buffer.partition(b'\n')
                return line.decode()
        return buffer.decode() 