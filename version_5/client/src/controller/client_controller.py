from threading import Thread
from .message_controller import MessageController
import json
from ..model import *
from ..view import ClientView
from ..service import WriterService

class ClientController:
    def __init__(self):
        ''' inicia toda a aplicacao criando cliente, interface e conexoes'''
        self.chats = {}
        self.online_users = []
        self.model = ClientModel()
        
        if not self.model.connected:
            print("cliente não iniciado")
            raise ConnectionError("Não foi possível conectar ao servidor.")

        self.view = ClientView(self)
        
        # Configura o listener para mensagens do servidor
        self.start_listening()
        
        # Inicia o processamento de mensagens
        self.view.after(100, self.process_messages)

    def setup_mvc(self):
        
        
        self.model = ClientModel()
        
        if not self.model.connected:
            print("cliente não iniciado")
            return 

        self.view = ClientView(self)
        
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
                        mensagem = MessageModel.receive_data(response)
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
                    WriterService.save_message(message)
                elif (message["type"] == "userlist"):
                    self.set_online_users(message["body"])
        # Agenda o próximo processamento
        self.view.after(100, self.process_messages)

    def create_chat(self, target):
        if target in self.chats:
            chat = self.chats[target]
            if hasattr(chat, "view") and chat.view.winfo_exists():
                chat.view.lift()
            else:
                del self.chats[target]
            return

        def thread_chat():
            chat = MessageController(self.model, target, self)
            self.chats[target] = chat
            self.view.after(0, chat.create_view)  # <- IMPORTANTE: Tkinter seguro aqui

        Thread(target=thread_chat, daemon=True).start()

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