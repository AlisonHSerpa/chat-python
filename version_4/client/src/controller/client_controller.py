from threading import Thread
from .message_controller import MessageController
import json

class ClientController:
    def __init__(self):
        self.model = None
        self.view = None
        self.chats = []
        self.setup_mvc()

    def setup_mvc(self):
        ''' inicia toda a plicacao criando cliente, interface e conexoes'''
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
                    response = self.model.socket.recv(1500)
                    if not response:
                        break

                    try:
                        mensagem= self.model.receive_data_server(response)
                        self.model.message_queue.put(mensagem)
                    except json.JSONDecodeError:
                        print("Erro ao decodificar mensagem")
                except Exception as e:
                    self.view.show_error(f'erro: {e}')
                    break
            self.model.connected = False
            self.view.show_error("desconectado do servidor")

        Thread(target=listen, daemon=True).start()

    def create_chat(self, destiny):
        """Generates a thread for each chat (each chat shares the main handler)."""
        def thread_chat():
            chat = MessageController(self.model, destiny)
            self.chats.append(chat)
            chat.create_view()

        # Start the thread (pass the function, don't call it!)
        thread = Thread(target=thread_chat)
        thread.daemon = True  # Optional: Kills thread when main program exits
        thread.start()

    def process_messages(self):
        """Processa mensagens na queue que o model RECEBE"""
        while not self.model.message_queue.empty():
            message = self.model.message_queue.get()

            if (message == "PING"):
                continue
            elif (message["type"] == "message"):
                if (message["to"] == self.model.username):
                    for chat in self.chats:
                        if (chat.destiny == message["from"]):
                            chat.post_message(message["body"])
                            break
                    self.notification.append(message)
        # Agenda o próximo processamento
        self.view.after(100, self.process_messages)

    # FASE DE TESTE
    def get_online_users(self):
        ''' pega a lista de usuarios online do servidor'''
        users = ["alison", "Arthur"]
        return users

    def disconnect(self):
        """Desconecta do servidor"""
        self.model.disconnect()

    def run(self):
        """Inicia a aplicação"""
        self.view.mainloop()