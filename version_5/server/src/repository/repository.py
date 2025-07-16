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
        self.messages.insert_one(message)

    '''metodos de busca'''
    def find_all_messages_by_username(self, username):
        messages_cursor = self.messages.find({"to": username}, {"_id": 0})
        messages_queue = Queue()

        for message in messages_cursor:
            messages_queue.put(message)
        
        return messages_queue
        
    def get_client_by_key(self, key):
        client = self.clients.find_one({"key": key})
        return client
    
    def get_client_by_username(self, username):
        client = self.clients.find_one({"username": username})
        return client
    
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
        # JSON simulando um cliente
        client_json = {
            "username": "alison",
            "key": "chave123"
        }

        # JSON simulando uma mensagem
        message_json = {
            "type": "text",
            "from": "alison",
            "to": "bob",
            "body": "Olá, Bob!"
        }

        # Inserir cliente
        repo.insert_client(client_json)
        print("Cliente inserido.")

        # Inserir mensagem
        repo.insert_message(message_json)
        print("Mensagem inserida.")

        # Buscar mensagens para bob
        messages = repo.find_all_messages_by_username("bob")

        while not messages.empty():
            msg = messages.get()
            print("Mensagem para bob:", msg)

        # Buscar cliente por chave
        client_by_key = repo.find_client_by_key("chave123")
        print("Cliente encontrado pela chave:", client_by_key)

        # Buscar cliente por username
        client_by_username = repo.find_client_by_username("alison")
        print("Cliente encontrado pelo nome:", client_by_username)

        # Editar nome do cliente
        if client_by_username:
            repo.edit_username_client(client_by_username, "alison_renomeado")
            print("Nome de usuário alterado.")

        # Deletar mensagens para bob
        repo.delete_messages_to_client("bob")
        print("Mensagens de 'bob' deletadas.")

        # Deletar cliente renomeado
        repo.delete_client_by_key("chave123")
        print("Cliente deletado.")
#'''
