import time
import threading
import os
from ..view import ChatView
from ..service import *
from ..model import *

class MessageController:
    def __init__(self, client_model, target, client_controller):
        self.model = client_model
        self.target = target
        self.view = None
        self.client_controller = client_controller
        self.diretorio = WriterService.get_chat_file_path(self.target)
        self.running = True
        self.update_thread = None
        self._chat_lock = threading.Lock()
        
        # chaves para encriptar
        self.peer_pub_key = None
        self.session_key = None

        # Garante que o arquivo existe de forma thread-safe
        WriterService.read_file(self.diretorio)

    def create_view(self):
        ''' Must be called from the main thread (Tkinter-safe) '''
        self.view = ChatView(self)
        
        # Inicia a thread de atualização
        self.update_thread = threading.Thread(target=self.update_chat, daemon=True)
        self.update_thread.start()
        
        return self.view

    def send_message(self):
        ''' pega o que foi digitado no label e envia para target dps coloca no txt '''
        body = self.view.get_message_input()
        if not body:
            return

        # Aqui cabe criptografar a mensagem
        criptografar = body # Esta variável vai chamar uma função que usa as chaves AES e HMAC para criptografar a mensagem.

        # Monta a mensagem
        message = MessageModel("message", self.model.username, self.target, criptografar)

        # Envia a mensagem
        MailService.send_to_mailman(message.get_message())

        # Mostra no chat e salva
        self.post_message(message.message)
        self.view.clear_message_input()

    def post_message(self, message):
        ''' coloca no txt de forma thread-safe '''
        with self._chat_lock:
            WriterService.save_own_message(message)
            self._update_chat_display()

    def _update_chat_display(self):
        ''' Atualiza o display do chat de forma thread-safe '''
        try:
            current_content = WriterService.read_file(self.diretorio)
            if current_content:
                self.view.display_message(current_content)
        except Exception as e:
            print(f"Erro ao atualizar chat: {e}")

    def update_chat(self):
        ''' Thread que verifica atualizações no arquivo de chat '''
        last_modified = 0
        while self.running:

            ''' 1 -
                    Pede a sessionKey para o SessionService
                    se não tiver pede a public key para o SessionService
            
            '''            

            # Primeiro, pede-se a SessionKey para a classe SessionService.
            self.session_key = SessionKeyService.request_session_key()

            if self.session_key is None:
                # A linha abaixo vai pedir a chave rsa pública do peer para o SessionService para usar temporariamente enquanto não poder estabelecer a sessão
                # self.peer_pub_key = 
                print()



            try:
                current_modified = os.path.getmtime(self.diretorio) if os.path.exists(self.diretorio) else 0
                if current_modified > last_modified:
                    with self._chat_lock:
                        self._update_chat_display()
                    last_modified = current_modified
            except Exception as e:
                print(f"Erro ao verificar atualizações do chat: {e}")
            time.sleep(1.5)
    
    def set_public_key(self, pub_key):
        self.public_key = pub_key

    def wait_pub_key(self):
        while not self.public_key:
            print("esperando public key...")

            # Verifica se a chave já está presente
            if self.target in self.client_controller.public_keys:
                return self.client_controller.public_keys[self.target]
            
            time.sleep(1.5)
            

    def stop(self):
        ''' Para a thread de atualização '''
        self.running = False
        if self.update_thread and self.update_thread.is_alive():
            self.update_thread.join(timeout=1)