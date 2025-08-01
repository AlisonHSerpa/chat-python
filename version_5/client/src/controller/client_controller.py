from threading import Thread
from .message_controller import MessageController
import json
from ..model import *
from ..view import ClientView
from ..service import WriterService
from ..controller import SessionController
from .mail_controller import MailController

class ClientController:
    def __init__(self):
        ''' inicia toda a aplicacao criando cliente, interface e conexoes'''
        self.chats = {}
        self.online_users = []
        self.model = ClientModel()
        
        # confere se o cliente foi bem iniciado, se n foi, fecha o programa
        if not self.model.connected:
            print("cliente não iniciado")
            raise ConnectionError("Não foi possível conectar ao servidor.")
        
        self.view = ClientView(self)

        # conecta
        MailController.connect_to_server()

        # threads de envio e recepção
        Thread(target=MailController.listen, daemon=True).start()
        Thread(target=MailController.deliver, daemon=True).start()

        # Loop para processar mensagens recebidas
        self.view.after(100, self.process_messages)

    def process_messages(self):
        ''' encaminha as mensagens do Mailbox para seus devidos tratamentos'''
        while not MailController.mailbox.empty():
            # pega uma mensagem que chegou no mailbox
            message = MailController.take_from_mailbox()

            # confere se a mensagem eh para voce
            if (message["to"] == self.model.username):

                if (message["type"] == "message"):
                    WriterService.save_message(message)

                elif (message["type"] == "session_key"): 
                    '''Esse método é chamado para receber a chave pública do 
                    destinatário para ser usada no Diffie-Hellman. Opcionalmente,
                    pode receber o salt e os parãmetros se o remetente tiver iniciado a sessão.'''

                    info = message["body"] # O body do json é armazenado em info.
                    
                    nome = message["from"] # O nome do remetente é armazenado em nome.
                    
                    SessionController.separar_dados_dh(info) # info é passado para o método que 
                    # separa os dados do Diffie-Hellman.
                
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