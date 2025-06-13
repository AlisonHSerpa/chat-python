import random
import tkinter as tk
from tkinter import scrolledtext, messagebox, simpledialog
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
from queue import Queue

class ChatClient(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Chat Cliente")
        self.geometry("400x600")
        self.username = self._generate_random_name()  # Nome aleatorio
        self.message_queue = Queue()  # Fila para comunicação entre threads
        self._setup_ui()
        self._setup_socket()
        self._set_username(self.username)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        self.after(100, self._process_messages)  # Verifica mensagens periodicamente

    # cuida do visual
    def _setup_ui(self):
        # frame principal
        main_frame = tk.Frame(self)
        main_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # Label do nome de usuário (com estilo melhorado)
        self.name_label = tk.Label(
            main_frame, 
            text=f'Usuário: {self.username}',
            font=('Arial', 10, 'bold'),
            bg='#f0f0f0',
            padx=5,
            pady=2
        )
        self.name_label.pack(fill=tk.X, pady=(0, 5))
        
        # Área de chat com scroll
        self.chat_area = scrolledtext.ScrolledText(
            main_frame,
            wrap=tk.WORD,
            state='disabled',
            font=('Arial', 10),
            padx=5,
            pady=5
        )
        self.chat_area.pack(fill=tk.BOTH, expand=True)
        
        # campo de mensagem
        self.message_entry = tk.Text(self, height=3)
        self.message_entry.pack(padx=10, pady=5, fill=tk.X)
        self.message_entry.bind("<Return>", lambda e: self._send_message())

        # caixa de botoes
        button_frame = tk.Frame(self)
        button_frame.pack(pady=5)
        
        self.send_button = tk.Button(button_frame, text="Enviar", command=self._send_message)
        self.send_button.pack(side=tk.LEFT, padx=5)
        
        self.name_button = tk.Button(button_frame, text="Mudar Nome", command=self._ask_username)
        self.name_button.pack(side=tk.LEFT, padx=5)

        self.command_button = tk.Button(button_frame, text="lista de comandos", command=self._command_list)
        self.command_button.pack(side=tk.LEFT, padx=6)

    # monstrar aba com lista de comandos
    def _command_list(self):
        help_window = tk.Tk()
        help_window.title("Command List")
        help_window.geometry("500x100")

        text = tk.Text(help_window, height=8)
        text.pack(padx=10, pady=10, expand=True,fill=tk.BOTH)

        text.insert(
            index='1.0', 
            chars= 'Mostrar usuários onlines: /list/users/ \n' 
            'Mandar mensagem privada: /whisper/<username>/<mensagem> \n' 
            'Mudar o nome: /change/name/<novo_nome>'
        )


    # Pede o nome do usuário
    def _ask_username(self):
        new_username = simpledialog.askstring("Nome", "Escolha seu nome:", parent=self)
        if new_username and new_username.strip():
            self.username = new_username.strip()
            self._show_message(f"Você agora é conhecido como: {self.username}")
            
            # Atualiza o label do nome
            self._set_username(new_username)

    def _set_username(self, username):
        self.name_label.config(text=f'Usuário: {username}')

        switchName = f'/change/name/{username}'
        self.socket_cliente.sendall(switchName.encode())

    def _generate_random_name(self):
       random_names = [
        "Luffy", "Brook", "Rocks", "Kuma", "Zoro", "Nami", "Robin", "Franky",
        "Sanji", "Usopp", "Chopper", "Jinbe", "Ace", "Sabo", "Gol D. Roger",
        "Shanks", "Buggy", "Mihawk", "Boa Hancock", "Bartholomew Kuma", 
        "Trafalgar Law", "Eustass Kid", "Killer", "Kaido", "Big Mom", 
        "Blackbeard", "Whitebeard", "Marco", "Izo", "Yamato", "Oden", 
        "Enel", "Crocodile", "Doflamingo", "Magellan", "Ivankov", 
        "Bon Clay", "Smoker", "Tashigi", "Fujitora", "Kizaru", "Aokiji", 
        "Akainu", "Garp", "Sengoku", "Koala", "Rebecca", "Shirahoshi", 
        "Vivi", "Carrot", "Pedro", "Kin'emon", "Denjiro", "Raizo", 
        "Kanjuro", "Monet", "Caesar Clown", "Vergo", "Corazon", "Pell", 
        "Wapol", "Hody Jones", "Arlong", "Bellamy", "Bartolomeo", 
        "Cavendish", "Basil Hawkins", "X Drake", "Scratchmen Apoo",
        "Urouge", "Capone Bege", "Shiki", "Zephyr", "Pudding", "Katakuri"
        ]
       return random.choice(random_names)

    # cuida da conexao
    def _setup_socket(self):
        try:
            self.socket_cliente = socket(AF_INET, SOCK_STREAM)
            self.socket_cliente.connect(('127.0.0.1', 8000))
            Thread(target=self._listen_server, daemon=True).start()

            # adicionar outra thread para listar usuarios
            
            self._show_message("Conectado ao servidor.")
        except Exception as e:
            self._show_message(f"Falha na conexão: {e}")

    # mandar mensagem
    def _send_message(self):
        message = f"{self.username}: " + self.message_entry.get("1.0", tk.END).strip()
        if not message or message == f"{self.username}: ":
            return

        try:
            self.socket_cliente.sendall(message.encode())
            if "/" not in message:
                self._show_message(message)
            self.message_entry.delete("1.0", tk.END)
        except Exception as e:
            self._show_message(f"Falha ao enviar: {e}")


    # cuida das entradas de mensagem
    def _listen_server(self):
        while True:
            try:
                response = self.socket_cliente.recv(1500).decode()
                if not response:
                    break
                self.message_queue.put(response)  # Adiciona mensagem na fila
            except Exception as e:
                self.message_queue.put(f"Conexão perdida: {e}")  # Adiciona erro na fila
                break
    
    # Processa mensagens da fila na thread principal
    def _process_messages(self):
        while not self.message_queue.empty():
            message = self.message_queue.get()
            self._show_message(message)
        self.after(100, self._process_messages)  # Agenda a próxima verificação

    # cuida da text area
    def _show_message(self, message):
        self.chat_area.config(state='normal')
        self.chat_area.insert(tk.END, f"{message}\n")
        self.chat_area.config(state='disabled')
        self.chat_area.yview(tk.END)

    # fecha conexao
    def _on_close(self):
        try:
            self.socket_cliente.close()
        except:
            pass
        self.destroy()

if __name__ == "__main__":
    app = ChatClient()
    app.mainloop()