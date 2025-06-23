from threading import Thread
import sys

class ServerController:
    def __init__(self, model):
        self.model = model
    
    def send_notification(self, notification):
        """Envia notificação para todos os clientes"""
        print(notification)
        for client in self.model.clients[:]:
            try:
                client.socket.sendall(notification.encode())
            except (ConnectionResetError, BrokenPipeError):
                # Remove cliente que não responde
                self.model.remove_client(client.socket)
                print(f"Cliente desconectado: {client.username}")
    
    def handle_new_connection(self, client_socket, client_address):
        """Processa a conexão inicial do cliente"""
        try:
            # Recebe o username inicial
            initial_data = client_socket.recv(1024).decode().strip()
            
            if initial_data.startswith("/setusername"):
                username = initial_data.split()[1]
                client = self.model.add_client(client_socket, client_address, username)
                self.broadcast_message(f"{username} entrou no chat. ", self.model.server_socket)
                self.broadcast_message(f"Bem-vindo, {username}!", self.model.server_socket)
                return client
            else:
                client_socket.close()
                return None
        except Exception as e:
            print(f"Erro ao configurar novo cliente: {e}")
            client_socket.close()
            return None
    
    def transmit_message(self, client_socket):
        """Gerencia a transmissão de mensagens de um cliente"""
        client = self.model.get_client_by_socket(client_socket)
        if not client:
            return
        
        print(f'Escutando o cliente: {client.username}')
        
        try:
            while True:
                mensagem = client_socket.recv(1500)
                if not mensagem:  # Cliente desconectou normalmente
                    break
                
                raw_message = mensagem.decode().strip()
                print(raw_message)
                self.broadcast_message(raw_message, client_socket)
        
        except ConnectionResetError:
            print(f"Conexão resetada pelo cliente: {client.username}")
        except Exception as e:
            print(f"Erro com cliente {client.username}: {e}")
        finally:
            removed_client = self.model.remove_client(client_socket)
            if removed_client:
                self.send_notification(f"{removed_client.username} saiu do chat.")
            client_socket.close()
    
    def broadcast_message(self, message, sender_socket=None):
        """Envia mensagem para todos os clientes exceto o remetente"""
        for client in self.model.clients[:]:
            if client.socket != sender_socket:
                try:
                    client.socket.sendall(message.encode())
                except (ConnectionResetError, BrokenPipeError):
                    self.model.remove_client(client.socket)
                    print(f"Cliente desconectado durante envio: {client.username}")
    
    def send_private_message(self, sender, target_username, message_body):
        """Envia mensagem privada entre usuários"""
        recipient = self.model.get_client_by_username(target_username)
        
        if recipient:
            msg = f"[Private from {sender.username}]: {message_body}"
            try:
                recipient.socket.sendall(msg.encode())
                sender.socket.sendall(f"[Private to {target_username}]: {message_body}".encode())
            except:
                sender.socket.sendall("Erro ao enviar mensagem privada".encode())
        else:
            sender.socket.sendall(f"Usuário '{target_username}' não encontrado ou offline".encode())
    
    def list_online_users(self, client_socket):
        """Envia lista de usuários online para o cliente solicitante"""
        users = self.model.get_online_users()
        formatted_users = "\n- " + "\n- ".join(users) if users else "Nenhum usuário online"
        message = f"Usuários online:{formatted_users}"
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
                client_socket, client_address = self.model.server_socket.accept()
                client = self.handle_new_connection(client_socket, client_address)
                if client:
                    Thread(target=self.transmit_message, args=(client_socket,)).start()

        except KeyboardInterrupt:
            print("\nDesligando servidor...")
            self.model.close_all()