from ..model import *
from queue import Queue
import json

class MessageController:
    def __init__(self, server, model, repository):
        self.server = server
        self.notification = Queue()
        self.model = model
        self.repository = repository
    
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
                    self.dispatch_message(json_data)

                except json.JSONDecodeError:
                    # Se não for um JSON válido
                    error_msg = MessageModel("error","server", json_data["from"], "Formato de dados inválido. Envie um JSON válido.")
                    client_socket.sendall(error_msg.get_message().encode())
                    client_socket.close()
                    return None
                except Exception as e:
                    print(f"Erro ao configurar novo cliente: {e}")
                    error_msg = MessageModel("error","server", json_data["from"],f"Erro interno do servidor: {str(e)}")
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

    
    ''' handlers '''
    def handle_message(self, origin, destiny, message, date, time, type = "message"):
        """Envia mensagem para o cliente"""
        print("chegou ate aqui")
        # verifica se os dois existem no banco de dados
        if not self.find_both_clients:
            print("verificaçao falhou")
            return

        # Criar o objeto de mensagem
        response = MessageModel(type, origin, destiny, message, date, time)

        # procura o destino
        destiny_client = None
        for client in self.model.clients:
            if client.username == destiny:
                destiny_client = client
                break

        if not destiny_client:
            # destino existe, mas está offline
            response.hold_message(self.repository)
            print(f"Mensagem para {destiny} armazenada como pendente.")
        else:
            # destino está online, envia direto via socket
            try:
                destiny_client.socket.sendall(response.get_message().encode())
                print(f"Mensagem enviada para {destiny}.")
            except Exception as e:
                print(f"Erro ao enviar mensagem para {destiny}: {e}")

    def handle_username(self, address, username):
        # ESSA CLASSE NAO ESTA SENDO USADA
        for client in self.model.clients:
            if client.address == address:
                client.setusername(username)
                return

    def handle_request(self, origin, target):
        # verifica se os dois existem no banco de dados
        if not self.find_both_clients:
            return

        # pega a key do target
        target_client = self.repository.get_client_by_username(target)
        target_key = target_client["key"]

        # monta a mensagem
        response = MessageModel("request_key", target, origin, target_key)

        # envia se a origem estiver onlinde
        for client in self.model.clients:
            if client.username == origin:
                client.socket.sendall(response.get_message().encode())
                return

        # se nao estiver online, armazena
        response.hold_message(self.repository)


    ''' metodos auxiliares '''
    # metodo para reenviar mensagens pendentes
    def retreive_old_messages(self, cliente):
        mensagens_pendentes = self.repository.find_and_delete_all_messages_by_username(cliente.username)

        while not mensagens_pendentes.empty():
            mensagem = mensagens_pendentes.get()
            cliente.socket.sendall(json.dumps(mensagem).encode())

    def find_both_clients(self, origin, destiny):
        try:
            # procura o objeto cliente de origem
            origin_client = self.repository.get_client_by_username(origin)
            if origin_client is None:
                print(f"Usuário de origem '{origin}' não encontrado.")
                return False

            target_client = self.repository.get_client_by_username(destiny)
            if target_client is None:
                print(f"Usuário de destino '{destiny}' não encontrado.")
                return False
            
            return True
        except Exception as e:
            print(f"Erro ao acessar o banco de dados: {e}")
            return False
        
    def dispatch_message(self, json_data):
        tipo = json_data.get("type")
        origem = json_data.get("from")
        destino = json_data.get("to")
        corpo = json_data.get("body")
        date = json_data.get("date")
        time = json_data.get("time")

        handlers = {
            "changeusername": lambda: self.handle_username(origem, corpo) if destino == "server" else None,
            "message": lambda: self.handle_message(origem, destino, corpo, date, time),
            "session_key": lambda: self.handle_message(origem, destino, corpo, date, time, tipo),
            "request_key": lambda: self.handle_request(origem, destino)
        }

        if tipo in handlers:
            return handlers[tipo]()  # Executa o handler
        else:
            print(f"[WARNING] Tipo de mensagem não reconhecido: {tipo}")
