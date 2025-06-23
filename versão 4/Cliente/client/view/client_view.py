import tkinter as tk
from tkinter import scrolledtext, messagebox, simpledialog

class ClientView(tk.Tk):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.title("Chat Cliente")
        self.geometry("400x600")
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self._setup_ui(self.controller.model.get_username())

    def _setup_ui(self, username):

        # Frame principal
        main_frame = tk.Frame(self)
        main_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # Label do nome de usuário
        self.name_label = tk.Label(
            main_frame, 
            text= f"Usuario : {username}",
            font=('Arial', 10, 'bold'),
            bg='#f0f0f0',
            padx=5,
            pady=2
        )
        self.name_label.pack(fill=tk.X, pady=(0, 5))
        
        # Área de chat
        self.chat_area = scrolledtext.ScrolledText(
            main_frame,
            wrap=tk.WORD,
            state='disabled',
            font=('Arial', 10),
            padx=5,
            pady=5
        )
        self.chat_area.pack(fill=tk.BOTH, expand=True)
        
        # Campo de mensagem
        self.message_entry = tk.Text(self, height=3)
        self.message_entry.pack(padx=10, pady=5, fill=tk.X)
        self.message_entry.bind("<Return>", lambda e: self.controller.send_message())

        # Frame de botões
        button_frame = tk.Frame(self)
        button_frame.pack(pady=5)
        
        self.send_button = tk.Button(button_frame, text="Enviar", command=self.controller.send_message)
        self.send_button.pack(side=tk.LEFT, padx=5)

        self.command_button = tk.Button(button_frame, text="Comandos", command=self.show_commands)
        self.command_button.pack(side=tk.LEFT, padx=6)

    def show_commands(self):
        commands = (
            "Mostrar usuários onlines: /list/users/\n"
            "Mandar mensagem privada: /whisper/<username>/<mensagem>\n"
            "Mudar o nome: /change/name/<novo_nome>"
        )
        messagebox.showinfo("Lista de Comandos", commands)

    def update_username_display(self, username):
        self.name_label.config(text=f'Usuário: {username}')

    def display_message(self, message):
        self.chat_area.config(state='normal')
        self.chat_area.insert(tk.END, f"{message}\n")
        self.chat_area.config(state='disabled')
        self.chat_area.yview(tk.END)

    def get_message_input(self):
        return self.message_entry.get("1.0", tk.END).strip()

    def clear_message_input(self):
        self.message_entry.delete("1.0", tk.END)

    def on_close(self):
        self.controller.disconnect()
        self.destroy()

    def show_error(self, message):
        messagebox.showerror("Erro", message)