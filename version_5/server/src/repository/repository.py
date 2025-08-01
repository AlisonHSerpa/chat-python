from dotenv import load_dotenv, find_dotenv
import os
from pymongo import MongoClient
from queue import Queue

load_dotenv(find_dotenv())

connection_string = os.environ.get("MONGO_CONNECTION_STRING")

'''
para esta classe funcionar, o database deve seguir essa arquitetura:
    nome do banco de dados:
    chat
        nome das colecoes:
        clients
        messages

estrutura dos jsons que vai ser salva:
    cliente
    {
        "username": "",
        "key": ""           # esse key eh de chave publica (criptografia assimetrica)
    }

    mensagem
    {
        "type": "",
        "from": "",
        "to": "",
        "body": ""
    }
OBS: importante deixar claro que ESSA CLASSE SUPOE QUE OS PARAMETROS SAO JSONS
'''

class Repository:
    def __init__(self):
        try:
            self.client = MongoClient(connection_string, serverSelectionTimeoutMS=5000)
            self.client.admin.command('ping')  # Testa a conexão
        except Exception as e:
            print("Erro ao conectar ao MongoDB:", e)
            self.client = None
            return

        self.db = self.client.chat
        self.clients = self.db.clients
        self.messages = self.db.messages

    '''metodos de insercao'''
    def insert_client(self, client):
        if not client.get("username") or not client.get("key"):
            raise ValueError("Cliente inválido")
        self.clients.insert_one(client)

    def insert_message(self, message):
        required_fields = {"type", "from", "to", "body", "date", "time"}
        if not required_fields.issubset(message.keys()):
            raise ValueError("Mensagem incompleta")
        self.messages.insert_one(message)

    '''metodos de busca'''
    def find_all_messages_by_username(self, username):
        messages_cursor = self.messages.find({"to": username}, {"_id": 0})
        messages_queue = Queue()

        for message in messages_cursor:
            messages_queue.put(message)
        
        return messages_queue
    
    def find_and_delete_all_messages_by_username(self, username):
        messages_queue = Queue()

        while True:
            # Busca e remove uma mensagem com "to" igual ao username
            message = self.messages.find_one_and_delete({"to": username}, projection={"_id": 0})
            if not message:
                break
            messages_queue.put(message)

        return messages_queue
        
    def get_client_by_key(self, key):
        client = self.clients.find_one({"key": key})
        return client
    
    def get_client_by_username(self, username):
        client = self.clients.find_one({"username": username})
        return client
    
    def get_all_clients(self):
        return [client["username"] for client in self.clients.find({}, {"_id": 0, "username": 1})]
    
    '''metodos de alteracao'''
    def edit_username_client(self, client, newName):
        self.clients.update_one({"username": client["username"]}, {"$set": {"username": newName}})

    '''metodos para deletar'''
    def delete_client_by_key(self, key):
        self.clients.delete_one({"key": key})

    def delete_messages_to_client(self, username):
        self.messages.delete_many({"to": username})


'''
# TESTE COM JSONS SIMULADOS

if __name__ == "__main__":
    repo = Repository()

    if repo.client is None:
        print("Falha na conexão, teste abortado.")
    else:
        print("Conectado ao MongoDB com sucesso.")

        # Inserir múltiplos clientes
        clients = [
            {"username": "alison", "key": "chave123"},
            {"username": "bob", "key": "chave456"},
            {"username": "carol", "key": "chave789"}
        ]

        for c in clients:
            repo.insert_client(c)
            print(f"Cliente inserido: {c['username']}")

        # Verificar todos os usernames
        usernames = repo.get_all_clients()
        print("Todos os clientes no banco:", usernames)

        # Inserir mensagens para diferentes destinatários
        mensagens = [
            {"type": "text", "from": "alison", "to": "bob", "body": "Oi Bob!"},
            {"type": "text", "from": "carol", "to": "bob", "body": "Bom dia Bob!"},
            {"type": "text", "from": "bob", "to": "alison", "body": "E aí Alison!"},
            {"type": "text", "from": "bob", "to": "carol", "body": "Olá Carol!"}
        ]

        for m in mensagens:
            repo.insert_message(m)
            print(f"Mensagem de {m['from']} para {m['to']} inserida.")

        # Buscar mensagens para 'bob' (sem deletar)
        print("\nMensagens destinadas a 'bob' (find_all_messages_by_username):")
        queue = repo.find_all_messages_by_username("bob")
        while not queue.empty():
            print(queue.get())

        # Buscar e deletar mensagens para 'carol'
        print("\nMensagens destinadas a 'carol' (find_and_delete_all_messages_by_username):")
        deleted_queue = repo.find_and_delete_all_messages_by_username("carol")
        while not deleted_queue.empty():
            print(deleted_queue.get())

        # Verificar se mensagens de 'carol' foram realmente deletadas
        remaining_carol = repo.find_all_messages_by_username("carol")
        print("Mensagens restantes para 'carol':", remaining_carol.qsize())

        # Buscar cliente por chave
        client_by_key = repo.get_client_by_key("chave123")
        print("\nCliente encontrado pela chave 'chave123':", client_by_key)

        # Buscar cliente por username
        client_by_username = repo.get_client_by_username("alison")
        print("Cliente encontrado pelo nome 'alison':", client_by_username)

        # Editar username do cliente 'alison' para 'alison_renomeado'
        if client_by_username:
            repo.edit_username_client(client_by_username, "alison_renomeado")
            print("Username de 'alison' alterado para 'alison_renomeado'.")

        # Verificar alteração
        renamed = repo.get_client_by_username("alison_renomeado")
        print("Cliente renomeado encontrado:", renamed)

        # Deletar todas as mensagens para 'alison_renomeado'
        repo.delete_messages_to_client("alison_renomeado")
        print("Mensagens de 'alison_renomeado' deletadas.")

        # Deletar todos os clientes (cleanup)
        for c in clients:
            repo.delete_client_by_key(c["key"])
            print(f"Cliente deletado: {c['username']}")
#'''
