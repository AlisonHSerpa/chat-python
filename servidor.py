from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread

# Worker para gerenciar a comunicação com o cliente
# metodo de falar com o cliente
def falarComCliente(cliente_socket, endereco_cliente):
    print(f'Conexão estabelecida com o {endereco_cliente}')

    while True:
        # Envia mensagem para o Cliente
        response = input("")
        cliente_socket.sendall(response.encode())

# metodo de receber mensagens do cliente
def escutarCliente(cliente_socket, endereco_cliente):
    print(f'escutando o cliente: {endereco_cliente}')

    while True:
        # Recebe mensagem do cliente
        mensagem = cliente_socket.recv(1500)

        # Se a mensagem nao chegar, encerra a conexao
        if not mensagem or mensagem.decode() == "encerrar chat":
            print("Nenhuma mensagem recebida, fechando conexao")
            #fecha a conexao com o cliente
            cliente_socket.close()

        # Receber mensagem do cliente
        print(f'Cliente:{mensagem.decode()}.')

# metodo para que o servidor aceite multiplos clientes


# configuracao do servidor
# cria o socket servidor
server_socket = socket(AF_INET, SOCK_STREAM)
# liga o servidor ao endereço IP e porta
server_socket.bind(('127.0.0.1', 8000))
# Coloca o servidor em modo de escuta
server_socket.listen()
print('Aguardando por novas requisiçõse na porta 8000')

# aceita a conexão
while True:
    cliente_socket, endereco_cliente = server_socket.accept()

    # criando thread de envio para o servidor
    Thread(target=falarComCliente, args=(cliente_socket, endereco_cliente)).start()
    # criando thread de recebimento para o servidor
    Thread(target=escutarCliente, args=(cliente_socket, endereco_cliente)).start()
