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
        ''' metodo para receber as mensagens de cada cliente individualmente'''
        client = self.model.get_client_by_socket(client_socket)
        if not client:
            print("listen() falhou")
            return
        
        print(f'Escutando o cliente: {client.address}')
        
        try:
            while True:
                mensagem = client_socket.recv(8096)
                if not mensagem:
                    break

                try:
                    json_data = self.model.receive_data_server(mensagem)
                    print(json_data)
                    self.dispatch_message(json_data)

                    print (json_data)
                except json.JSONDecodeError:
                    print("Mensagem inválida (JSONDecodeError). Ignorando, mas mantendo conexão.")
                    continue  # Não fecha o socket, apenas ignora essa mensagem

                except Exception as e:
                    print(f"Erro ao processar mensagem de {client.username}: {e}")
                    continue  # Continua ouvindo sem fechar

        except ConnectionResetError:
            print(f"Conexão resetada pelo cliente: {client.username}")
        except Exception as e:
            print(f"Erro com cliente {client.username}: {e}")
        finally:
            self.model.remove_client(client_socket)
            client_socket.close()


    
    ''' handlers '''
    def handle_message(self, json_data):
        """Envia mensagem para o cliente"""
        print("chegou ate o handle")

        target = json_data.get("to")
        origin = json_data.get("from")

        # verifica se os dois existem no banco de dados
        if not self.find_both_clients(origin, target):
            print("verificaçao falhou")
            return

        # procura o destino
        destiny_client = None
        for client in self.model.clients:
            if client.username == target:
                destiny_client = client
                break

        if not destiny_client:
            # destino existe, mas está offline
            self.repository.insert_message(json_data)
            print(f"Mensagem para {target} armazenada como pendente.")
        else:
            # destino está online, envia direto via socket
            try:
                destiny_client.socket.sendall(json.dumps(json_data).encode())
                print(f"Mensagem enviada para {target}.")
            except Exception as e:
                print(f"Erro ao enviar mensagem para {target}: {e}")

    def handle_dh(self, json_data):
        """Trata mensagens DH_1 e DH_2 sem encerrar a conexão"""
        origin = json_data.get("from")
        target = json_data.get("to")

        print("chegou no handle_dh")

        # Garante que ambos existam no banco
        if not self.find_both_clients(origin, target):
            print(f"Handshake de {origin} para {target} falhou: usuário não encontrado.")
            # Armazena para quando o destino se conectar
            self.repository.insert_message(json_data)
            return

        # Procura destino online
        destiny_client = next((c for c in self.model.clients if c.username == target), None)
        if destiny_client:
            try:
                destiny_client.socket.sendall(json.dumps(json_data).encode())
                print(f"Handshake {json_data['type']} enviado para {target}.")
            except Exception as e:
                print(f"Erro ao enviar handshake para {target}: {e}")
                self.repository.insert_message(json_data)
        else:
            print(f"Destino {target} offline. Handshake armazenado.")
            self.repository.insert_message(json_data)


    def handle_username(self, address, username):
        # ESSA CLASSE NAO ESTA SENDO USADA
        for client in self.model.clients:
            if client.address == address:
                client.setusername(username)
                return

    def handle_request(self, origin, target):
        # verifica se os dois existem no banco de dados

        print("chegou em handle_request")

        if not self.find_both_clients:
            return
        
        print("passou pelo find_both")

        # pega a key do target
        target_client = self.repository.get_client_by_username(target)
        target_key = target_client["key"]

        # monta a mensagem
        response = MessageModel("request_key", target, origin, target_key)
        print(response)

        # envia se a origem estiver onlinde
        for client in self.model.clients:
            if client.username == origin:
                client.socket.sendall(response.get_message().encode())
                print("enviado de volta")
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
        key = json_data.get("key")
        param = json_data.get("param")
        aes = json_data.get("aes")
        iv = json_data.get("iv")
        date = json_data.get("date")
        time = json_data.get("time")
        

        print("chegou no servidor")
        handlers = {
            "changeusername": lambda: self.handle_username(origem, corpo) if destino == "server" else None,
            "message": lambda: self.handle_message(json_data),
            "DH_1": lambda: self.handle_dh(json_data),
            "DH_2": lambda: self.handle_dh(json_data),
            "request_key": lambda: self.handle_request(origem, destino)
        }

        if tipo in handlers:
            handlers[tipo]()  # Executa o handler
        else:
            print(f"[WARNING] Tipo de mensagem não reconhecido: {tipo}")
