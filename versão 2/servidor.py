from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
from threading import Thread
import tkinter as tk
from tkinter import scrolledtext

# configuracao do servidor
# cria o socket servidor
server_socket = socket(AF_INET, SOCK_STREAM)
# liga o servidor ao endereço IP e porta
server_socket.bind(('127.0.0.1', 8000))
# Coloca o servidor em modo de escuta
server_socket.listen()
print('Aguardando por novas conexões na porta 8000')

# array de clientes
clientes = []

# loop de conexao
def connection_request():
    # aceita a conexão
    while True:
        # aceita conexoes e salva os usuarios que entrarem
        cliente_socket, endereco_cliente = server_socket.accept()
        clientes.append(cliente_socket)

        # notificar que alguem novo chegou no chat
        send_notification(notification = f'{endereco_cliente} entrou no chat')

        # criando thread de envio de mensagem do servidor
        Thread(target=send_message).start()
        # criando thread de retransmissao de mensagem
        Thread(target=transmit_message, args=(cliente_socket, endereco_cliente)).start()

# metodo de falar com todos os clientes sem distincao
def send_notification(notification):
    print(notification)    
    # Envia mensagem para todos os Clientes
    for i in clientes:
        i.sendall(notification.encode())


# metodo de receber mensagens de um cliente e retransmitir para os outros
def transmit_message(cliente_socket, endereco_cliente):
    print(f'escutando o cliente: {endereco_cliente}')

    while True:
        # Recebe mensagem do cliente
        mensagem = cliente_socket.recv(1500)
        mensagemGlobal = (f'{endereco_cliente}:{mensagem.decode()}.')
        print(mensagemGlobal)

        # nao envia para o cliente que mandou a mensagem
        for i in clientes:
            if i != cliente_socket:
                i.sendall(mensagemGlobal.encode())

def send_message():
    while True:
        # Envia mensagem para o Cliente
        response = input("")

        for i in clientes:
            i.sendall(f' Servidor: {response}'.encode())
            

connection_request()
