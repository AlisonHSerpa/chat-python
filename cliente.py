from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread

# worker para gerenciar a comunicação com o Servidor
# mandar mensagem para o Servidor
def falarComServidor (socket_cliente):
    while True:
        # envia mensagem
        message = input("")
        socket_cliente.sendall(message.encode())

        # criterio de parada eh "encerrar chat"
        if (message == "encerrar chat"):
            socket_cliente.sendall("Cliente desconectado".encode())
            print("chat encerrado")
            socket_cliente.close()

# metodo para receber mensagens do servidor
def escurtarServidor (socket_cliente):
    while True:
        # Recebe mensagem
        response = socket_cliente.recv(1500)
        print(f'Servidor:{response.decode()}')

# configuracao do cliente
# cria o socket
socket_cliente = socket(AF_INET, SOCK_STREAM)
print(f'pronto para conectar ao servidor na porta 8000')
# conecta ao servidor
socket_cliente.connect(('127.0.0.1', 8000))
print("conectado no servidor, criterio de parada eh: 'encerrar chat'") 

# criando thread de envio para cliente
Thread(target=falarComServidor, args=(socket_cliente,)).start()
# criando thread de recebimento para cliente
Thread(target=escurtarServidor, args=(socket_cliente,)).start()