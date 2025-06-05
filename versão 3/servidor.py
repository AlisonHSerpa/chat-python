from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
import sys

# Configuração do servidor
server_socket = socket(AF_INET, SOCK_STREAM)
server_socket.bind(('127.0.0.1', 8000))
server_socket.listen()
print('Aguardando por novas conexões na porta 8000')

# Lista de clientes
clientes = []

# Função para enviar notificações
def send_notification(notification):
    print(notification)
    # Envia mensagem para todos os clientes
    for cliente in clientes[:]:  # Usamos uma cópia da lista para evitar problemas durante iteração
        try:
            cliente.sendall(notification.encode())
        except (ConnectionResetError, BrokenPipeError):
            # Remove cliente que não responde
            clientes.remove(cliente)
            print(f"Cliente desconectado: {cliente.getpeername()}")

# Função para transmitir mensagens entre clientes
def transmit_message(cliente_socket, endereco_cliente):
    print(f'Escutando o cliente: {endereco_cliente}')
    
    try:
        while True:
            # Recebe mensagem do cliente
            mensagem = cliente_socket.recv(1500)
            if not mensagem:  # Cliente desconectou normalmente
                break
                
            mensagemGlobal = f'{endereco_cliente}: {mensagem.decode()}'
            print(mensagemGlobal)

            # Envia para todos os outros clientes
            for cliente in clientes[:]:
                if cliente != cliente_socket:
                    try:
                        cliente.sendall(mensagemGlobal.encode())
                    except (ConnectionResetError, BrokenPipeError):
                        clientes.remove(cliente)
                        print(f"Cliente desconectado durante envio: {cliente.getpeername()}")
    
    except ConnectionResetError:
        print(f"Conexão resetada pelo cliente: {endereco_cliente}")
    except Exception as e:
        print(f"Erro com cliente {endereco_cliente}: {e}")
    finally:
        # Remove cliente da lista e fecha socket
        if cliente_socket in clientes:
            clientes.remove(cliente_socket)
        cliente_socket.close()
        send_notification(f'{endereco_cliente} saiu do chat')

# Função para enviar mensagens do servidor
def send_message():
    while True:
        try:
            response = input("Servidor: ")
            if response.lower() == 'sair':
                for cliente in clientes[:]:
                    cliente.close()
                server_socket.close()
                sys.exit(0)
                
            send_notification(f'Servidor: {response}')
        except Exception as e:
            print(f"Erro ao enviar mensagem do servidor: {e}")

# Loop principal de conexão
def connection_request():
    try:
        while True:
            cliente_socket, endereco_cliente = server_socket.accept()
            clientes.append(cliente_socket)
            print(f'Nova conexão de: {endereco_cliente}')
            
            send_notification(f'{endereco_cliente} entrou no chat')
            
            Thread(target=transmit_message, args=(cliente_socket, endereco_cliente)).start()
    except KeyboardInterrupt:
        print("\nDesligando servidor...")
        for cliente in clientes:
            cliente.close()
        server_socket.close()

# Inicia threads
Thread(target=send_message, daemon=True).start()
connection_request()