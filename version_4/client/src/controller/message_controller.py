from ..view import ChatView
import time
from threading import Thread

class MessageController:
    def __init__(self, model, target, client_controller):
        self.model = model
        self.target = target
        self.view = None
        self.client_controller = client_controller
        self.diretorio = f"./chats/{self.target}.txt"
        self.running = True

    def create_view(self):
        ''' Must be called from the main thread (Tkinter-safe) '''
        # inicia a UI do chat
        self.view = ChatView(self)

        # atualizar o chat
        update_thread = Thread(target=self.update_chat, daemon=True)
        update_thread.start()

        return self.view

    def send_message(self):
        ''' pega o que foi digitado no label e envia para target dps coloca no txt '''
        message = self.view.get_message_input()
        if not message:
            return
        
        # envia a mensagem
        self.model.send_message(self.target , message)

        # mostra no chat
        self.post_message(message)
        self.view.clear_message_input()

    def post_message(self, message):
        ''' coloca no txt '''
        line = f"{self.model.username} : {message}"
        self.model.writer.add_line(self.diretorio, line)

        # Atualiza imediatamente o chat na interface
        try:
            current_content = self.model.writer.read_file(self.diretorio)
            if current_content:
                self.view.display_message(current_content)
        except Exception as e:
            print(f"Erro ao atualizar chat após envio: {e}")

    def update_chat(self):
        last_content = ""
        while self.running:
            try:
                current_content = self.model.writer.read_file(self.diretorio)
                if current_content is not None and current_content != last_content:
                    self.view.display_message(current_content)
                    last_content = current_content
            except Exception as e:
                print(f"Erro ao atualizar chat: {e}")
            time.sleep(1.5)

    def __del__(self):
        self.running = False