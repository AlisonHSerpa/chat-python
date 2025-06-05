from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
import sys

# Configuração do servidor
server_socket = socket(AF_INET, SOCK_STREAM)
server_socket.bind(('172.29.9.195', 8000))
server_socket.listen()
print('Aguardando por novas conexões na porta 8000')

# Lista de clientes
clientes = []
socket_to_username = {}

# Função para enviar notificações
def _send_notification(notification):
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
def _transmit_message(cliente_socket, endereco_cliente):
    print(f'Escutando o cliente: {endereco_cliente}')
    
    try:
        while True:
            # Recebe mensagem do cliente
            mensagem = cliente_socket.recv(1500)
            if not mensagem:  # Cliente desconectou normalmente
                break
            
            # tratamento de mensagem do servidor
            rawMensagem = mensagem.decode()
            if "/" in rawMensagem:
                _process_command(rawMensagem, endereco_cliente, cliente_socket)
                continue
            
            # tratamento de mensagem antes do envio global
            print(rawMensagem)

            # Envia para todos os outros clientes
            for cliente in clientes[:]:
                if cliente != cliente_socket:
                    try:
                        cliente.sendall(rawMensagem.encode())
                    except (ConnectionResetError, BrokenPipeError):
                        clientes.remove(cliente)
                        print(f"Cliente desconectado durante envio: {cliente.getpeername()} - {socket_to_username.get(endereco_cliente)}")
    
    except ConnectionResetError:
        print(f"Conexão resetada pelo cliente: {endereco_cliente} - {socket_to_username.get(endereco_cliente)}")
    except Exception as e:
        print(f"Erro com cliente {endereco_cliente} - {socket_to_username.get(endereco_cliente)}: {e}")
    finally:
        if cliente_socket in clientes:
            clientes.remove(cliente_socket)  # Remove da lista de sockets ativos
            username = socket_to_username.pop(endereco_cliente, None)  # Remove do mapeamento
            if username:
                print(f"{username} saiu do chat.")
                _send_notification(f"{username} saiu do chat.")  # Apenas notifica o chat, sem enviar lista
        cliente_socket.close()

# processa uma mensagem que possui comandos do cliente
def _process_command(raw_command, client_address, client_socket):
    try:
        parts = raw_command.split("/", 3)
        if len(parts) != 4:
            raise ValueError("Formato incorreto! Use: /comando/alvo/mensagem")
        
        _, command, target, body = parts

        if command.lower() == "change":
            _client_name_map(client_address, body)
            client_socket.sendall("Nome atualizado com sucesso!".encode())
            
        elif command.lower() == "whisper":
            _private_send(client_socket, client_address, target, body)
        
        elif command.lower() == "list":
            _list_online_users(client_socket)
        else:
            raise ValueError("Comando desconhecido")
            
    except Exception as e:
        error_msg = f"Erro: {str(e)}"
        client_socket.sendall(error_msg.encode())

# mapeia os usuarios nos sockets
def _client_name_map(client_address, body):
    socket_to_username[client_address] = str(body)

# envia uma lista de usuarios online
def _list_online_users(client_socket):
    users = [name for name in socket_to_username.values()]
    # Formata a lista de usuários com "-" antes de cada nome
    formatted_users = "\n-".join(users) if users else "Nenhum usuário online"
    message = f"usuarios online:\n-{formatted_users}"
    client_socket.sendall(message.encode())

def _private_send(sender_socket, client_address, target_username, message_body):
    # Verifica se o remetente tem nome cadastrado
    sender_username = socket_to_username.get(client_address)
    if not sender_username:
        sender_socket.sendall("Você precisa definir um nome primeiro com /name".encode())
        return
    
    # Procura o socket do destinatário
    recipient_socket = None
    for socket in clientes:
        try:
            socket_address = socket.getpeername()
            if socket_address in socket_to_username:
                if socket_to_username[socket_address].lower() == target_username.lower():
                    recipient_socket = socket
                    break
        except:
            continue
    
    if recipient_socket:
        msg = f"[Private from {sender_username}]: {message_body}"
        try:
            recipient_socket.sendall(msg.encode())
            sender_socket.sendall(f"[Private for {target_username}]: {message_body} ".encode())
        except:
            sender_socket.sendall("Erro ao enviar mensagem privada".encode())
    else:
        sender_socket.sendall(f"Usuário '{target_username}' não encontrado ou offline".encode())

# Função para enviar mensagens do servidor
def _send_message():
    while True:
        try:
            response = input("Servidor: ")
            if response.lower() == 'sair':
                for cliente in clientes[:]:
                    cliente.close()
                server_socket.close()
                sys.exit(0)
                
            _send_notification(f'Servidor: {response}')
        except Exception as e:
            print(f"Erro ao enviar mensagem do servidor: {e}")

# Loop principal de conexão
def _connection_request():
    try:
        while True:
            cliente_socket, endereco_cliente = server_socket.accept()
            clientes.append(cliente_socket)
            print(f'Nova conexão de: {endereco_cliente}')
            
            _send_notification(f'{endereco_cliente} entrou no chat')
            
            Thread(target=_transmit_message, args=(cliente_socket, endereco_cliente)).start()
    except KeyboardInterrupt:
        print("\nDesligando servidor...")
        for cliente in clientes:
            cliente.close()
        server_socket.close()

# Inicia threads
Thread(target=_send_message, daemon=True).start()
_connection_request()