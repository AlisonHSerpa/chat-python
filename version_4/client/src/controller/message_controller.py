from ..view import ChatView

class MessageController:
    def __init__(self, model, target, client_controller):
        self.model = model
        self.target = target
        self.view = None
        self.client_controller = client_controller

    def create_view(self):
        ''' Must be called from the main thread (Tkinter-safe) '''
        self.view = ChatView(self)
        return self.view

    def send_message(self):
        ''' pega o que foi digitado no label e envia para target '''
        message = self.view.get_message_input()
        if not message:
            return

        formatted = f"{self.model.username}: {message}"

        # envia a mensagem
        self.model.send_message(self.target , message)

        # mostra no chat
        self.view.display_message(formatted)
        self.view.clear_message_input()

    def post_message(self, message):
        ''' coloca no textbox '''
        self.view.display_message(message)

