---

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
* `pymongo` (driver oficial MongoDB para Python)
* `python-dotenv` (para carregar variáveis do arquivo `.env`)

---

## 🚀 Como Executar (Deploy Local)

### 1. 📥 Clone o repositório

```bash
git clone https://github.com/AlisonHSerpa/chat-python.git
cd chat-python/version_4
```

### 2. 📦 Instale as dependências

As bibliotecas nativas do Python já vêm instaladas, mas para integrar com o MongoDB e usar o `.env`, instale as bibliotecas extras:

```bash
pip install pymongo python-dotenv
```

---

## ⚙️ Configuração do Ambiente (.env)

Este projeto utiliza um arquivo `.env` para armazenar informações sensíveis, como a string de conexão do MongoDB. Por segurança, o arquivo `.env` **não está versionado** e deve ser criado manualmente.

### Como criar o arquivo `.env`

Na raiz do projeto, crie um arquivo chamado `.env` com o seguinte conteúdo (exemplo):

```
MONGO_CONNECTION_STRING=mongodb+srv://usuario:senha_codificada@seucluster.mongodb.net/nomeDoBanco?retryWrites=true&w=majority
```

> **Importante:**
>
> * Se sua senha contém caracteres especiais, **ela deve estar URL-encoded** na string (exemplo: `@` vira `%40`, `#` vira `%23`).
> * Você pode usar o Python para fazer o encode da senha com o módulo `urllib.parse.quote_plus()`.

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
