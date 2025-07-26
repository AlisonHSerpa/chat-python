import tkinter as tk
from tkinter import scrolledtext, messagebox

class ChatView(tk.Toplevel):  # Ou tk.Tk se for a janela principal
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.title("Chat")
        self.geometry("400x600")
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self._setup_ui()

    def _setup_ui(self):
        # Frame principal
        main_frame = tk.Frame(self)
        main_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # Label do nome de usuário
        self.name_label = tk.Label(
            main_frame, 
            text=f"Conversando com : {self.controller.target}",
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
        self.message_entry.bind("<Return>", self._on_enter_pressed)

        # Frame de botões
        button_frame = tk.Frame(self)
        button_frame.pack(pady=5)
        
        self.send_button = tk.Button(button_frame, text="Enviar", command=self.controller.send_message)
        self.send_button.pack(side=tk.LEFT, padx=5)

    def update_username_display(self, username):
        self.name_label.config(text=f'conversando com : {username}')

    def display_message(self, message):
        """Exibe o conteúdo completo do chat no text box"""
        try:
            if not isinstance(message, str):
                message = str(message)

            self.chat_area.config(state='normal')
            self.chat_area.delete("1.0", tk.END)  # limpa tudo
            self.chat_area.insert(tk.END, message)
            self.chat_area.see(tk.END)
            self.chat_area.config(state='disabled')

        except Exception as e:
            print(f"Error displaying message: {e}")


    def get_message_input(self):
        return self.message_entry.get("1.0", tk.END).strip()

    def clear_message_input(self):
        self.message_entry.delete("1.0", tk.END)

    def on_close(self):
        self.controller.__del__()
        self.destroy()

    def show_error(self, message):
        messagebox.showerror("Erro", message)

    def _on_enter_pressed(self, event):
        self.controller.send_message()
        return "break"