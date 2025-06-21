from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
 
# O cliente irá se conectar ao servidor e se identificar logo de início
# O cliente irá informar um nome que ainda não exista no dicionário self.clients (servidor)
# O cliente irá informar para qual outro cliente quer enviar a mensagem
# Ou seja, o cliente irá informar o nome do destinatário e a mensagem
# O cliente poderá receber mensagens do servidor (simultaneamente)
 
class Cliente:
    def __init__(self, host, port=12345):
        self.host = host
        self.port = port
        self.client_socket = socket(AF_INET, SOCK_STREAM)
        self.client_name = "Alison"
 
    def start(self):
        self.client_socket.connect((self.host, self.port))
        print("[*] Conectado ao servidor")
        # logo no inicio o cliente precisará se identificar
        # enquanto o servidor não aceitar o nome, o cliente não poderá continuar
        while True:
            try:
                self.client_name = input("Informe seu nome: ")
                self.client_socket.send(self.client_name.encode('utf-8'))
                response = self.client_socket.recv(1024).decode('utf-8')
                if response == "Nome já existe. Tente outro.":
                    print(response)
                elif response == "Nome aceito":
                    print(f"[*] Nome {self.client_name} aceito")
                    break
                else:
                    print("Resposta inesperada do servidor! Desligando...")
                    self.client_socket.close()
                    exit(1)
            except Exception as e:
                print(f"Erro: {e}")
 
        # iniciar uma thread secundária para receber mensagens do servidor
        receive_thread = Thread(target=self.receive_messages)
        receive_thread.start()
 
        # enquanto o cliente estiver conectado, ele poderá enviar mensagens
        # para outros clientes, na thread principal
        while True:
            try:
                recipient_name = input("Informe o nome do destinatário: ")
                message = input("Informe a mensagem: ")
                # a mensagem será no formato "destinatário:mensagem"
                self.client_socket.send(f"{recipient_name}:{message}".encode('utf-8'))
            except Exception as e:
                print(f"Erro: {e}")
                break
 
    def receive_messages(self):
        # enquanto o cliente estiver conectado, ele poderá receber mensagens
        # do servidor, na thread secundária
        while True:
            try:
                message = self.client_socket.recv(1024).decode('utf-8')
                if not message:
                    break
                print(f"\n[**]{message}")
            except Exception as e:
                print(f"Erro: {e}")
                break
 
if __name__ == "__main__":
    # criar um cliente e iniciar a conexão com o servidor
    cliente = Cliente(host = "172.29.9.204")
    cliente.start()