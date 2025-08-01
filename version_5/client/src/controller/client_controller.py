import sys
from threading import Thread
from .message_controller import MessageController
from ..model import *
from ..view import ClientView
from ..service import*
from .session_controller import SessionController
from ..security import *

class ClientController:
    def __init__(self):
        ''' inicia toda a aplicacao criando cliente, interface e conexoes'''
        # conecta
  
        if not MailService.connect_to_server():
            print("Falha ao conectar ao servidor.")
            raise ConnectionError("Não foi possível conectar ao servidor.")
        
        try:
            self.model = ClientModel()

            if not isinstance(self.model.username, str):
                self.disconnect()
        except Exception as e:
            print(f"Falha ao iniciar o cliente: {e}")
            MailService.disconnect()
        
        self.chats = {}
        self.online_users = []

        self.view = ClientView(self)

        # threads de envio e recepção
        Thread(target=MailService.listen, daemon=True).start()
        Thread(target=MailService.deliver, daemon=True).start()

        # Loop para processar mensagens recebidas
        self.view.after(100, self.process_messages)

    def process_messages(self):
        ''' encaminha as mensagens do Mailbox para seus devidos tratamentos'''
        while not MailService.mailbox.empty():
            # pega uma mensagem que chegou no mailbox
            message = MailService.take_from_mailbox()

            # confere se a mensagem eh para voce
            if (message["to"] == self.model.username):

                if (message["type"] == "message"):
                    message['body'] = Encrypt_DH.recebe_mensagem(message['body'])
                    WriterService.save_message()

                elif (message["type"] == "session_key"): 
                    '''Esse método é chamado para receber a chave pública do 
                    destinatário, o salt e os parâmetros para serem usados no Diffie-Hellman.'''

                    return_message = SessionController.separar_dados_dh(message["body"], message["nome"]) 
                    
                    # Enfim, é enviada a chave pública para o destinatário.
                    MailService.socket.sendall(return_message.get_message().encode())

                elif (message["type"] == "session_key_response"):
                    '''Esse método é chamado para receber APENAS a chave pública do remetente.'''

                    SessionController.separar_dados_dh(message["body"], message["nome"])
                
                elif (message["type"] == "userlist"):
                    self.set_online_users(message["body"])

                elif (message["type"] == "request_key"):
                    print(message)
                    # chama o sessionkeyservice para guardar
                    SessionKeyService.insert_rsa_public_key(message["from"], message["body"])

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
        # Para todas as threads dos chats
        for chat in self.chats.values():
            chat.stop()  # <- garante que a thread de cada chat seja encerrada
        
        # para as threads de MailService
        MailService.stop()

        # MailService.socket.close()
        MailService.disconnect()
        
        # disconnecta model
        self.model.disconnect()
        
        # fecha o programa
        sys.exit(1)

    def run(self):
        """Inicia a aplicação"""
        self.view.mainloop()