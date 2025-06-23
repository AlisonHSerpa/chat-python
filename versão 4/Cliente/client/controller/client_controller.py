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
        
        # Configura o listener para mensagens do servidor
        self.model.start_listening(self.handle_server_message)
        
        # Inicia o processamento de mensagens
        self.view.after(100, self.process_messages)

    def send_message(self):
        """Envia mensagem para o servidor"""
        message = self.view.get_message_input()
        if not message:
            return
        
        # Mensagem normal
        full_message = f"{self.model.username}: {message}"
        result = self.model.send_message(full_message)
        
        if result is not True:
            self.view.show_error(result)
        else:
            self.view.display_message(full_message)
            self.view.clear_message_input()

    def handle_server_message(self, message):
        """Processa mensagens recebidas do servidor"""
        self.model.message_queue.put(message)

    def process_messages(self):
        """Processa mensagens na fila e atualiza a view"""
        while not self.model.message_queue.empty():
            message = self.model.message_queue.get()

            if (message != "PING"):
                # Mensagem normal do chat
                self.view.display_message(message)
        
        # Agenda o próximo processamento
        self.view.after(100, self.process_messages)

    def disconnect(self):
        """Desconecta do servidor"""
        self.model.disconnect()

    def run(self):
        """Inicia a aplicação"""
        self.view.mainloop()