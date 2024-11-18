from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
import tkinter as tk
from tkinter import scrolledtext

#tela da interface
class MainView(tk.Tk):
    def __init__(self):
        #heranca
        super().__init__()

        #tamanho e titulo
        self.title("Chat Interface cliente")
        self.geometry("400x500")

        # Área de mensagens (ScrolledText)
        self.chat_area = scrolledtext.ScrolledText(self, wrap=tk.WORD, state='disabled')
        self.chat_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Área de texto para entrada de mensagem
        self.message_entry = tk.Text(self, height=3)
        self.message_entry.pack(padx=10, pady=5, fill=tk.X)

        # Botão "Enviar"
        self.send_button = tk.Button(self, text="Enviar", command=self.send_message)
        self.send_button.pack(pady=5)

        # configuracao da conexao com o servidor
        # cria o socket
        self.socket_cliente = socket(AF_INET, SOCK_STREAM)
        print(f'pronto para conectar ao servidor na porta 8000')
        # conecta ao servidor
        self.socket_cliente.connect(('127.0.0.1', 8000))

        # criando thread de envio para cliente
        Thread(target=self.send_message).start()
        # criando thread de recebimento para cliente
        Thread(target=self.escurtarServidor).start()


    def send_message(self):
        # Obtém o texto da área de entrada
        message = self.message_entry.get("1.0", tk.END).strip()
        if message:
            # Habilita a area de chat para editar
            self.chat_area.config(state='normal')
            self.chat_area.insert(tk.END, f"Você: {message}\n") #edita
            self.chat_area.config(state='disabled')  # Desabilita para edição
            self.chat_area.yview(tk.END)  # Rola para o fim

            # Limpa a área de entrada
            self.message_entry.delete("1.0", tk.END)
        
        self.socket_cliente.sendall(message.encode())

    # metodo para receber mensagens do servidor
    def escurtarServidor (self):
        while True:
            # Recebe mensagem
            response = self.socket_cliente.recv(1500)

            # habilita a area de chat para editar
            self.chat_area.config(state='normal')
            self.chat_area.insert(tk.END, f"{response.decode()} \n") #edita
            self.chat_area.config(state='disabled')  # Desabilita para edição
            self.chat_area.yview(tk.END)  # Rola para o fim

#inicia a aplicacao
if __name__ == "__main__":
    app = MainView()
    app.mainloop()