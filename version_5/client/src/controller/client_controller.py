from threading import Thread
from .message_controller import MessageController
import json

class ClientController:
    def __init__(self):
        self.model = None
        self.view = None
        self.chats = []
        self.online_users = []
        self.setup_mvc()

    def setup_mvc(self):
        ''' inicia toda a aplicacao criando cliente, interface e conexoes'''
        from ..model import ClientModel
        from ..view import ClientView
        
        self.model = ClientModel()
        self.view = ClientView(self)
        
        # Conecta ao servidor
        connection_result = self.model.connect_to_server()
        if connection_result is not True:
            self.view.show_error(f"Falha na conexão: {connection_result}")
            return
        
        # Configura o listener para mensagens do servidor
        self.start_listening()
        
        # Inicia o processamento de mensagens
        self.view.after(100, self.process_messages)

    def start_listening(self):
        ''' escuta as mensagens e coloca elas na queue do model'''
        def listen():
            while self.model.connected:
                try:
                    response = self.model.socket.recv(1500).decode()
                    if not response:
                        break

                    try:
                        mensagem= self.model.receive_data(response)
                        self.model.message_queue.put(mensagem)
                    except json.JSONDecodeError:
                        print("Erro ao decodificar mensagem")
                        break
                except Exception as e:
                    self.view.show_error(f'erro: {e}')
                    break
            self.model.connected = False
            self.view.show_error("desconectado do servidor")

        Thread(target=listen, daemon=True).start()

    def process_messages(self):
        """Processa mensagens na queue que o model RECEBE"""
        while not self.model.message_queue.empty():
            message = self.model.message_queue.get()
            if (message["to"] == self.model.username):
                if (message["type"] == "message"):
                    self.model.writer.notification.put(message)
                    self.model.writer.read_notification()
                elif (message["type"] == "userlist"):
                    self.set_online_users(message["body"])
        # Agenda o próximo processamento
        self.view.after(100, self.process_messages)

    def create_chat(self, target):
        """Generates a thread for each chat (each chat shares the main handler)."""
        def thread_chat():
            chat = MessageController(self.model, target, self)
            chat.create_view()

        # Start the thread (pass the function, don't call it!)
        thread = Thread(target=thread_chat)
        thread.daemon = True  # Optional: Kills thread when main program exits
        thread.start()

    def set_online_users(self, server_users):
        ''' pega a lista de usuarios online do servidor'''
        self.online_users = server_users
        
        # Notifica a view para atualizar a interface
        if self.view:
            self.view.update_online_users(self.online_users)

        return self.online_users
    
    def get_online_users(self):
        return self.online_users

    def disconnect(self):
        """Desconecta do servidor"""
        self.model.disconnect()

    def run(self):
        """Inicia a aplicação"""
        self.view.mainloop()