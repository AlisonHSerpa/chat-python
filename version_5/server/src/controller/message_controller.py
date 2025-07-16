from ..model import *
from socket import socket, AF_INET, SOCK_STREAM
from queue import Queue
import json

class MessageController:
    def __init__(self, server, model):
        self.server = server
        self.notification = Queue()
        self.model = model
    
    def listen(self, client_socket):
        """Gerencia a transmissão de mensagens de um cliente"""
        client = self.model.get_client_by_socket(client_socket)
        if not client:
            print("listen() falhou")
            return
        
        print(f'Escutando o cliente: {client.address}')
        
        try:
            while True:
                mensagem = client_socket.recv(1500)

                try:
                    json_data = self.model.receive_data_server(mensagem)

                    # faz o tratamento adequado para cada tipo de mensagem
                    if json_data.get("type") == "changeusername" and json_data.get("to") == "server":
                        self.handle_username(json_data["from"], json_data["body"])
                    if json_data.get("type") == "message" and json_data.get("to") != None:
                        self.handle_message(json_data["from"], json_data["to"], json_data["body"])

                except json.JSONDecodeError:
                    # Se não for um JSON válido
                    error_msg = MessageModel("error","server","unknown", "Formato de dados inválido. Envie um JSON válido.")
                    client_socket.sendall(error_msg.get_message().encode())
                    client_socket.close()
                    return None
                except Exception as e:
                    print(f"Erro ao configurar novo cliente: {e}")
                    error_msg = MessageModel("error","server","unkown",f"Erro interno do servidor: {str(e)}")
                    try:
                        client_socket.sendall(error_msg.get_message().encode())
                    except:
                        pass
                    client_socket.close()
                    return None
        except ConnectionResetError:
            print(f"Conexão resetada pelo cliente: {client.username}")
        except Exception as e:
            print(f"Erro com cliente {client.username}: {e}")
        finally:
            self.model.remove_client(client_socket)
            client_socket.close()

    def handle_message(self, origin, destiny, message):
        """Envia mensagem para o cliente"""

        # procura o objeto cliente de origem
        origin_client = self.model.get_client_by_username(origin)
        destiny_client = self.model.get_client_by_username(destiny)

        if not origin_client or not destiny_client:
            print("Usuário de origem ou destino não encontrado.")
            return

        response = MessageModel("message", origin, destiny, message)
        destiny_client.socket.sendall(response.get_message.encode())

    def handle_username(self, address, username):
        for client in self.model.clients:
            if client.address == address:
                client.setusername(username)
                break