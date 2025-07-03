import tkinter as tk
from tkinter import messagebox
import os

def ask_username():
    """
    Abre uma janela Tkinter para o usuário digitar seu nome.
    Retorna o nome digitado ou None se cancelado.
    """
    username = None  # Valor padrão se nada for digitado

    def save_and_close():
        nonlocal username
        username = entry_username.get().strip()
        
        if not username:
            messagebox.showwarning("Aviso", "Por favor, digite um nome válido!")
            return
        
        window.destroy()  # Fecha a janela

    # Configuração da janela
    window = tk.Tk()
    window.title("Cadastro de Usuário")
    window.geometry("300x150")

    # Label
    tk.Label(
        window,
        text="Por favor, digite seu nome:",
        font=("Arial", 10)
    ).pack(pady=10)

    # Entry
    entry_username = tk.Entry(window, width=30, font=("Arial", 10))
    entry_username.pack(pady=5)
    entry_username.focus()

    # Botão
    tk.Button(
        window,
        text="Confirmar",
        command=save_and_close,
        bg="#4CAF50",
        fg="white",
        font=("Arial", 10)
    ).pack(pady=10)

    # Mantém a janela aberta e aguarda interação
    window.mainloop()
    
    return username  # Retorna o nome ou None