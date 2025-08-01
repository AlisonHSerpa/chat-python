from socket import socket, AF_INET, SOCK_STREAM
from queue import Queue
from ..model import *
import json

class MailController:

    host='127.0.0.1'
    port=8000
    socket = socket(AF_INET, SOCK_STREAM)

    # ´feito para RETIRAR mensagens a serem recebidas [JSON]
    mailbox = Queue()

    # feito para ENVIAR mensagens a serem enviadas [MESSAGEMODEL]
    mailman = Queue()

    @staticmethod
    def connect_to_server():
        '''Conecta ao servidor'''
        try:
            MailController.socket.connect((MailController.host, MailController.port))
        except Exception as e:
            print(f'Erro ao conectar: {e}')
            return str(e)

    @staticmethod
    def listen():
        '''Recebe todas as mensagens e coloca na mailbox'''
        while True:
            try:
                response = MailController.socket.recv(1500).decode()
                if not response:
                    break
                try:
                    mensagem = MessageModel.receive_data(response)
                    MailController.mailbox.put(mensagem)
                except json.JSONDecodeError:
                    print("Erro ao decodificar mensagem JSON")
                    break
            except Exception as e:
                print(f'Erro ao escutar o servidor: {e}')                    
                break

    @staticmethod
    def deliver():
        '''Pega mensagens da fila mailman e envia pelo socket'''
        while True:
            try:
                mensagem = MailController.mailman.get(block=True)
                MailController.socket.send(mensagem.get_message().encode())

            except Exception as e:
                print(f'Erro ao enviar mensagem: {e}')
                break
    
    @staticmethod
    def send_to_mailman(message : MessageModel):
        ''' COLOCA na fila uma mensagem para ENVIO'''
        MailController.mailman.put(message)

    @staticmethod
    def take_from_mailbox():
        ''' RETIRA da fila uma mensagem RECEBIDA'''
        return MailController.mailbox.get()
    
