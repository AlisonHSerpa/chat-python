import time
import threading
import os
from ..view import ChatView
from ..service import *
from ..model import *
from ..security import Encrypt_DH

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
        criptografar = Encrypt_DH.prepare_send_message_dh(body) # Esta variável vai chamar uma função que usa as chaves AES e HMAC para criptografar a mensagem.

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
            '''
            if not self.peer_pub_key:
                self.peer_pub_key = self.wait_pub_key()
                print(self.peer_pub_key)

            try:
                current_modified = os.path.getmtime(self.diretorio) if os.path.exists(self.diretorio) else 0
                if current_modified > last_modified:
                    with self._chat_lock:
                        self._update_chat_display()
                    last_modified = current_modified
            except Exception as e:
                print(f"Erro ao verificar atualizações do chat: {e}")
            time.sleep(0.8)

    def wait_pub_key(self):
        while True:
            print("esperando public key...")
            rsa_pub_key = SessionKeyService.verificar_rsa_pub_key(self.model.username, self.target)
            if rsa_pub_key:
                return rsa_pub_key
            time.sleep(0.5)
            

    def stop(self):
        ''' Para a thread de atualização '''
        self.running = False
        if self.update_thread and self.update_thread.is_alive():
            self.update_thread.join(timeout=1)