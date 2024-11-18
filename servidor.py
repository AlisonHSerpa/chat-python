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
print('Aguardando por novas requisiçõse na porta 8000')

clientes = {}
count = 0

#interface
def connection_request():
    global count
    # aceita a conexão
    while True:
        cliente_socket, endereco_cliente = server_socket.accept()
        print(f'conectado com {endereco_cliente}')
        
        clientes[cliente_socket] = (endereco_cliente, count)

        # criando thread de envio para o servidor
        Thread(target=send_message, args=(cliente_socket)).start()
        # criando thread de recebimento para o servidor
        Thread(target=escutarCliente, args=(cliente_socket, endereco_cliente)).start()

# metodo de falar com o cliente
def send_message(cliente_socket):
    while True:
        # Envia mensagem para o Cliente
        response = input("")
        for i in clientes:
            cliente_socket.sendall(response.encode())

# metodo de receber mensagens do cliente
def escutarCliente(cliente_socket, endereco_cliente):
    print(f'escutando o cliente: {endereco_cliente}')

    while True:
        # Recebe mensagem do cliente
        mensagem = cliente_socket.recv(1500)
        mensagemGlobal = (f'{endereco_cliente}:{mensagem.decode()}.')

        for i in clientes:
            if i != cliente_socket:
                i.sendall(mensagemGlobal.encode())
            

connection_request()
