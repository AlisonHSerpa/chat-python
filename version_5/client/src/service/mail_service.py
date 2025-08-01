from socket import socket, AF_INET, SOCK_STREAM
from queue import Queue
import json
import time

class MailService:

    # ip do servidor
    host='127.0.0.1'
    port=8000

    # tipo de socket
    socket = socket(AF_INET, SOCK_STREAM)

    # feito para RETIRAR mensagens a serem recebidas [JSON]
    mailbox = Queue()

    # feito para ENVIAR mensagens a serem enviadas [JSON]
    mailman = Queue()

    # para fechar o programa direito
    running = True

    @staticmethod
    def connect_to_server():
        '''Conecta ao servidor'''
        try:
            MailService.socket = socket(AF_INET, SOCK_STREAM)
            MailService.socket.connect((MailService.host, MailService.port))
            return True
        except Exception as e:
            print(f'Erro ao conectar: {e}')
            return False

    @staticmethod
    def listen():
        '''Recebe todas as mensagens e coloca na mailbox'''
        while MailService.running:
            try:
                response = MailService.socket.recv(1500).decode()
                if not response:
                    break
                try:
                    mensagem = json.loads(response)
                    MailService.mailbox.put(mensagem)
                except json.JSONDecodeError:
                    print("Erro ao decodificar mensagem JSON")
                    break
            except Exception as e:
                print(f'Erro ao escutar o servidor: {e}')                    
                break

    @staticmethod
    def deliver():
        '''Pega mensagens da fila mailman e envia pelo socket'''
        while MailService.running:
            try:
                mensagem = MailService.mailman.get(block=True)
                MailService.socket.send(mensagem.encode())

            except Exception as e:
                print(f'Erro ao enviar mensagem: {e}')
                break
    
    @staticmethod
    def send_to_mailman(message):
        ''' COLOCA na fila uma mensagem para ENVIO'''
        MailService.mailman.put(message)

    @staticmethod
    def take_from_mailbox():
        ''' RETIRA da fila uma mensagem RECEBIDA'''
        return MailService.mailbox.get()
    
    @staticmethod
    def disconnect():
        MailService.socket.close()

    @staticmethod
    def stop():
        MailService.running = False
        time.sleep(0.5)