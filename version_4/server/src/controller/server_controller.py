from threading import Thread
import sys
import json
import time

class ServerController:
    def __init__(self, model):
        self.model = model

    def handle_new_connection(self, client_socket, client_address):
        """Processa a conexão inicial do cliente"""
        try:
            # Recebe o handshake de username
            data = client_socket.recv(1500).decode()
            mensagem = json.loads(data)
        
            if not mensagem["type"] == "changeusername":
                raise ValueError("protocolo invalido, username nao informado")
                
            username = mensagem["body"]
            self.model.add_client(client_socket, client_address, username)
            print(f"Novo cliente conectado: {username} ({client_address})")
            return client_socket
        except Exception as e:
            print(f"Erro ao configurar novo cliente: {e}")
            client_socket.close()
            return None
    
    def connection_request_loop(self):
        """Aceita novas conexões de clientes"""
        try:
            while True:
                client_socket, client_address = self.model.server_socket.accept()
                client = self.handle_new_connection(client_socket, client_address)
                if client:
                    Thread(target=self.listen, args=(client_socket,)).start()

        except KeyboardInterrupt:
            print("\nDesligando servidor...")
            self.model.close_all()

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
                    error_msg = {
                        "type": "error",
                        "from": "server",
                        "to": "unknown",
                        "body": "Formato de dados inválido. Envie um JSON válido."
                    }
                    client_socket.sendall(json.dumps(error_msg).encode())
                    client_socket.close()
                    return None
                except Exception as e:
                    print(f"Erro ao configurar novo cliente: {e}")
                    error_msg = {
                        "type": "error",
                        "from": "server",
                        "to": "unknown",
                        "body": f"Erro interno do servidor: {str(e)}"
                    }
                    try:
                        client_socket.sendall(json.dumps(error_msg).encode())
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

        json_message = {
            "type": "message",
            "from": origin,
            "to": destiny,
            "body": message
        }

        destiny_client.socket.sendall(json.dumps(json_message).encode())

    def handle_username(self, origin_socket, username):
        for client in self.model.clients:
            if client.socket == origin_socket:
                client.setusername(username)
                break

    def list_online_users(self):
        while True:
            users = [client.username for client in self.model.clients]
            message = {
                "type": "userlist",
                "from": "server",
                "to": "all",
                "body": users
            }
            for client in list(self.model.clients):
                try:
                    message["to"] = client.username
                    client.socket.sendall(json.dumps(message).encode())
                except Exception:
                    self.model.clients.remove(client)
            time.sleep(5)
