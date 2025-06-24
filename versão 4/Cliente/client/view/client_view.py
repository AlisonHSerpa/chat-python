import tkinter as tk
from tkinter import scrolledtext, messagebox, simpledialog
from .chat_view import ChatView

class ClientView(tk.Tk):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.title("Cliente")
        self.geometry("400x600")
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self._setup_ui(self.controller.model.username)

    def _setup_ui(self, username):
        # Frame principal
        main_frame = tk.Frame(self)
        main_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # Label do nome de usuário
        self.name_label = tk.Label(
            main_frame, 
            text=f"Usuário: {username}",
            font=('Arial', 10, 'bold'),
            bg='#f0f0f0',
            padx=5,
            pady=2
        )
        self.name_label.pack(fill=tk.X, pady=(0, 10))

        # Lista de usuários online
        self.listbox = tk.Listbox(
            main_frame,
            height=6,
            selectmode=tk.SINGLE
        )
        self.listbox.pack(padx=10, pady=10, expand=True, fill=tk.BOTH, side=tk.LEFT)
        
        # Atualiza a lista de usuários
        self.update_online_users(self.controller.get_online_users())
        
        # Vincula o evento de seleção
        self.listbox.bind('<<ListboxSelect>>', self._on_user_selected)

        v_scrollbar = tk.Scrollbar(
            main_frame,
            orient=tk.VERTICAL,
            command=self.listbox.yview
        )
        self.listbox['yscrollcommand'] = v_scrollbar.set
        v_scrollbar.pack(pady=10, side=tk.RIGHT, fill=tk.Y)

    def _on_user_selected(self, event):
        """Método chamado quando um usuário é selecionado na lista"""
        selected_index = self.listbox.curselection()
        if selected_index:  # Verifica se há algo selecionado
            selected_user = self.listbox.get(selected_index[0])
            self.controller.create_chat(selected_user)

    def update_online_users(self, users):
        """Atualiza a lista de usuários online"""
        self.listbox.delete(0, tk.END)
        for user in users:
            self.listbox.insert(tk.END, user)

    def update_username_display(self, username):
        self.name_label.config(text=f'Usuário: {username}')

    def on_close(self):
        self.controller.disconnect()
        self.destroy()

    def show_error(self, message):
        messagebox.showerror("Erro", message)