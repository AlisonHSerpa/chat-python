from threading import Thread

class ClientController:
    def __init__(self):
        self.model = None
        self.view = None
        self.setup_mvc()

    def setup_mvc(self):
        from ..model import ClientModel
        from ..view import ClientView
        
        self.model = ClientModel()
        self.view = ClientView(self)
        
        # Conecta ao servidor
        connection_result = self.model.connect_to_server()
        if connection_result is not True:
            self.view.show_error(f"Falha na conexão: {connection_result}")
            return
        
        # Configura o nome inicial
        self.change_username(self.model.username)
        
        # Inicia a escuta do servidor
        self.model.start_listening(self.handle_server_message)
        
        # Inicia o processamento de mensagens
        self.view.after(100, self.process_messages)

    def change_username(self, new_username=None):
        if new_username is None:
            new_username = self.view.get_message_input()
            if not new_username:
                return
        
        self.model.username = new_username
        self.model.send_message(f'/change/name/{new_username}')
        self.view.update_username_display(new_username)

    def send_message(self):
        message = self.view.get_message_input()
        if not message:
            return
        
        full_message = f"{self.model.username}: {message}"
        result = self.model.send_message(full_message)
        
        if result is not True:
            self.view.show_error(result)
        else:
            if "/" not in message:  # Não exibe mensagens de comando
                self.view.display_message(full_message)
            self.view.clear_message_input()

    def handle_server_message(self, message):
        self.model.message_queue.put(message)

    def process_messages(self):
        while not self.model.message_queue.empty():
            message = self.model.message_queue.get()
            self.view.display_message(message)
        self.view.after(100, self.process_messages)

    def disconnect(self):
        self.model.disconnect()

    def run(self):
        self.view.mainloop()