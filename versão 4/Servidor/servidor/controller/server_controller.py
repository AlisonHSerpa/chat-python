from threading import Thread
import sys

class ServerController:
    def __init__(self, model):
        self.model = model
    
    def send_notification(self, notification):
        """Envia notificação para todos os clientes"""
        print(notification)
        for cliente in self.model.clientes[:]:
            try:
                cliente.sendall(notification.encode())
            except (ConnectionResetError, BrokenPipeError):
                # Remove cliente que não responde
                self.model.clientes.remove(cliente)
                print(f"Cliente desconectado: {cliente.getpeername()}")
    
    def transmit_message(self, cliente_socket, endereco_cliente):
        """Gerencia a transmissão de mensagens de um cliente"""
        print(f'Escutando o cliente: {endereco_cliente}')
        
        try:
            while True:
                mensagem = cliente_socket.recv(1500)
                if not mensagem:  # Cliente desconectou normalmente
                    break
                
                rawMensagem = mensagem.decode()
                if "/" in rawMensagem:
                    self.process_command(rawMensagem, endereco_cliente, cliente_socket)
                    continue
                
                print(rawMensagem)
                self.broadcast_message(rawMensagem, cliente_socket)
        
        except ConnectionResetError:
            print(f"Conexão resetada pelo cliente: {endereco_cliente} - {self.model.get_username(endereco_cliente)}")
        except Exception as e:
            print(f"Erro com cliente {endereco_cliente} - {self.model.get_username(endereco_cliente)}: {e}")
        finally:
            username = self.model.remove_client(cliente_socket, endereco_cliente)
            if username:
                self.send_notification(f"{username} saiu do chat.")
            cliente_socket.close()
    
    def broadcast_message(self, message, sender_socket=None):
        """Envia mensagem para todos os clientes exceto o remetente"""
        for cliente in self.model.clientes[:]:
            if cliente != sender_socket:
                try:
                    cliente.sendall(message.encode())
                except (ConnectionResetError, BrokenPipeError):
                    self.model.clientes.remove(cliente)
                    print(f"Cliente desconectado durante envio: {cliente.getpeername()}")
    
    def process_command(self, raw_command, client_address, client_socket):
        """Processa comandos recebidos dos clientes"""
        try:
            parts = raw_command.split("/", 3)
            if len(parts) != 4:
                raise ValueError("Formato incorreto! Use: /comando/alvo/mensagem")
            
            _, command, target, body = parts

            if command.lower() == "change":
                self.model.map_username(client_address, body)
                client_socket.sendall("Nome atualizado com sucesso!".encode())
                
            elif command.lower() == "whisper":
                self.send_private_message(client_socket, client_address, target, body)
            
            elif command.lower() == "list":
                self.list_online_users(client_socket)
            else:
                raise ValueError("Comando desconhecido")
                
        except Exception as e:
            error_msg = f"Erro: {str(e)}"
            client_socket.sendall(error_msg.encode())
    
    def send_private_message(self, sender_socket, client_address, target_username, message_body):
        """Envia mensagem privada entre usuários"""
        sender_username = self.model.get_username(client_address)
        if not sender_username:
            sender_socket.sendall("Você precisa definir um nome primeiro com /name".encode())
            return
        
        recipient_socket = self.model.get_recipient_socket(target_username)
        
        if recipient_socket:
            msg = f"[Private from {sender_username}]: {message_body}"
            try:
                recipient_socket.sendall(msg.encode())
                sender_socket.sendall(f"[Private for {target_username}]: {message_body} ".encode())
            except:
                sender_socket.sendall("Erro ao enviar mensagem privada".encode())
        else:
            sender_socket.sendall(f"Usuário '{target_username}' não encontrado ou offline".encode())
    
    def list_online_users(self, client_socket):
        """Envia lista de usuários online para o cliente solicitante"""
        users = self.model.get_online_users()
        formatted_users = "\n-".join(users) if users else "Nenhum usuário online"
        message = f"usuarios online:\n-{formatted_users}"
        client_socket.sendall(message.encode())
    
    def server_message_loop(self):
        """Loop para envio de mensagens do servidor"""
        while True:
            try:
                response = input("Servidor: ")
                if response.lower() == 'sair':
                    self.model.close_all()
                    sys.exit(0)
                    
                self.send_notification(f'Servidor: {response}')
            except Exception as e:
                print(f"Erro ao enviar mensagem do servidor: {e}")
    
    def connection_request_loop(self):
        """Aceita novas conexões de clientes"""
        try:
            while True:
                cliente_socket, endereco_cliente = self.model.server_socket.accept()
                self.model.add_client(cliente_socket, endereco_cliente)
                
                self.send_notification(f'{endereco_cliente} entrou no chat')
                
                Thread(target=self.transmit_message, args=(cliente_socket, endereco_cliente)).start()

        except KeyboardInterrupt:
            print("\nDesligando servidor...")
            self.model.close_all()