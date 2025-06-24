# 💬 Chat Cliente-Servidor com Python + Tkinter

Este projeto é uma aplicação de chat simples baseada em **comunicação socket TCP com threads**, desenvolvida em **Python**, com uma interface gráfica usando **Tkinter**.

Você pode executar o projeto em dois modos:

* **Servidor**
* **Cliente (com GUI em Tkinter)**

A arquitetura é modular e se encontra organizada na pasta `version_4/`.

---

## 🛠️ Tecnologias Utilizadas

* Python 3.8+
* `socket` (módulo nativo)
* `threading` (módulo nativo)
* `tkinter` (módulo nativo para GUI)

---

## 🚀 Como Executar (Deploy Local)

### 1. 📥 Clone o repositório

```bash
git clone https://github.com/AlisonHSerpa/chat-python.git
cd chat-python/version_4
```

### 2. 📦 Instale as dependências

As bibliotecas utilizadas são todas nativas do Python, então nenhuma instalação via pip é necessária. Basta garantir que o Python esteja instalado corretamente.

> ✅ Requisitos:
>
> * Python 3.8 ou superior instalado.
> * Tkinter instalado (vem por padrão com Python em muitas distribuições).

---

## 🖥️ Como Rodar

### 🧠 Rodar o Servidor

Abra um terminal, navegue até o diretório do servidor e execute:

```bash
cd version_4/server
python main.py
```

O servidor ficará escutando novas conexões de clientes.

---

### 🧑‍💻 Rodar o Cliente

Em outro terminal (ou máquina diferente), navegue até o diretório do cliente e execute:

```bash
cd version_4/client
python main.py
```

A interface gráfica será aberta, permitindo que você envie mensagens para os demais clientes conectados.

---

## 📸 Demonstração

> *adicionar prints da interface depois*

---

## 📂 Estrutura do Projeto

```
version_3/
├── client.py
└── server.py
version_4/
├── client/
│   ├── main.py
│   └── client/
│       ├── controller/
│             ├── __init__.py
│             ├── client_controller.py
│             └── message_controller.py
│       ├── model/
│             ├──__init__.py
│             └── client_model.py
│       ├── view/
│             ├──__init__.py
│             ├── client_view.py
│             └── chat_view.py
│       └── __init__.py
│
└── server/
    ├── main.py
    └── server
       ├── controller
             ├── __init__.py
             ├── server_controller.py
       ├── model
             ├──__init__.py
             └── server_model.py
       └── __init__.py
```

---

## 🧑‍🤝‍🧑 Contribuindo

Sinta-se livre para abrir *issues* ou *pull requests* se quiser contribuir com melhorias!

---

## 📝 Licença

Este projeto está sob a licença MIT.

---
