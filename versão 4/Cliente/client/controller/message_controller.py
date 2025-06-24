from ..view import ChatView

class MessageController:
    def __init__(self, model, target):
        self.model = model
        self.target = target
        self.view = None

    def create_view(self):
        """Must be called from the main thread (Tkinter-safe)."""
        self.view = ChatView(self)
        return self.view

    def send_message(self):
        message = self.view.get_message_input()
        if not message:
            return

        formatted = f"{self.model.username}: {message}"
        result = self.model.mount_message("message",self.target, message)

        if result is not True:
            self.view.show_error(f"erro ao enviar a mensagem: {result}")
        else:
            self.view.display_message(formatted)
            self.view.clear_message_input()

    def post_message(self, message):
        self.view.display_message(message)

