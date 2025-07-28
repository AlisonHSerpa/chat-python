import os
import json
import threading

# TODOS OS TIPOS DE RETORNO E ENTRADAS SAO JSONS OU STR
class WriterService:
    BASE_DIR = os.path.dirname(os.path.abspath(os.path.join(__file__, "..", "..")))
    DATA_DIR = os.path.join(BASE_DIR, "data")
    _file_locks = {}  # Dicionário para armazenar locks por arquivo
    _lock = threading.Lock()  # Lock para operações no dicionário de locks

    @staticmethod
    def _get_file_lock(filepath):
        ''' metodo auxiliar para pegar os paths corretos'''
        with WriterService._lock:
            if filepath not in WriterService._file_locks:
                WriterService._file_locks[filepath] = threading.Lock()
            return WriterService._file_locks[filepath]

    @staticmethod
    def write_client(json_data=None, diretorio=None):
        ''' cria um arquivo user.txt para salvar dados do cliente atual'''
        if diretorio is None:
            diretorio = WriterService.get_user_file_path()

        folder = os.path.dirname(diretorio)
        if not os.path.exists(folder):
            os.makedirs(folder)

        if json_data is None:
            raise ValueError("erro ao tentar ler usuario")

        file_lock = WriterService._get_file_lock(diretorio)
        with file_lock:
            try:
                with open(diretorio, 'w', encoding='utf-8') as file:
                    json.dump(json_data, file, indent=4)
            except Exception as e:
                raise RuntimeError(f"Erro ao escrever o arquivo JSON: {e}")

    @staticmethod
    def read_client(diretorio=None):
        ''' le o arquivo user.txt para pegar os dados do cliente atual'''
        if diretorio is None:
            diretorio = WriterService.get_user_file_path()

        file_lock = WriterService._get_file_lock(diretorio)
        with file_lock:
            try:
                with open(diretorio, 'r', encoding='utf-8') as file:
                    data = json.load(file)

                required_fields = ["username", "private_key", "public_key", "local_key"]
                for field in required_fields:
                    if field not in data:
                        raise ValueError(f"Campo '{field}' ausente no arquivo.")

                return {
                    "username": data["username"],
                    "private_key": data["private_key"],
                    "public_key": data["public_key"],
                    "local_key": data["local_key"]
                }
            except FileNotFoundError:
                raise FileNotFoundError(f"Arquivo '{diretorio}' não encontrado.")
            except json.JSONDecodeError:
                raise ValueError(f"O conteúdo do arquivo '{diretorio}' não é um JSON válido.")
            except Exception as e:
                raise RuntimeError(f"Erro ao ler arquivo JSON: {e}")

    @staticmethod
    def write_session(json_session_key, username, path_file=None, modo='w'):
        ''' cria um arquivo para a session key ficar salva'''
        if path_file is None:
            path_file = WriterService.get_session_file_path(username)

        file_lock = WriterService._get_file_lock(path_file)
        with file_lock:
            try:
                dir_path = os.path.dirname(path_file)
                if dir_path and not os.path.exists(dir_path):
                    os.makedirs(dir_path)

                with open(path_file, modo, encoding='utf-8') as arquivo:
                    arquivo.write(json_session_key)
                return True
            except Exception as e:
                print(f"Erro ao escrever no arquivo: {e}")
                return False
            
    @staticmethod
    def get_session_key(username):
        ''' pega o arquivo da session key, que eh nomeado pelo nome do cliente alvo'''
        diretorio = WriterService.get_session_file_path(username)

        file_lock = WriterService._get_file_lock(diretorio)
        with file_lock:
            try:
                with open(diretorio, 'r', encoding='utf-8') as file:
                    data = json.load(file)

                return {
                    "username": data["username"],
                    "key": data["key"],
                    "creation_time": data["creation_time"],
                    "expiration_seconds": data["expiration_seconds"],
                    "remaining_messages": data["remaining_messages"],
                    "valid": data["valid"]
                }
            except FileNotFoundError:
                raise FileNotFoundError(f"Arquivo '{diretorio}' não encontrado.")
            except json.JSONDecodeError:
                raise ValueError(f"O conteúdo do arquivo '{diretorio}' não é um JSON válido.")
            except Exception as e:
                raise RuntimeError(f"Erro ao ler arquivo JSON: {e}")

    @staticmethod
    def read_file(path_file, default_content=""):
        ''' le os arquivos que guardam o historico de mensagens'''
        file_lock = WriterService._get_file_lock(path_file)
        with file_lock:
            try:
                if os.path.exists(path_file):
                    with open(path_file, 'r', encoding='utf-8') as arquivo:
                        return arquivo.read()
                else:
                    dir_path = os.path.dirname(path_file)
                    if dir_path and not os.path.exists(dir_path):
                        os.makedirs(dir_path)
                    
                    with open(path_file, 'w', encoding='utf-8') as arquivo:
                        arquivo.write(default_content)
                    return default_content
            except Exception as e:
                print(f"Erro ao ler/criar arquivo: {e}")
                return None

    @staticmethod
    def _add_line(file_path, line):
        ''' metodo auxiliar para escrever uma nova mensagens no historico'''
        file_lock = WriterService._get_file_lock(file_path)
        with file_lock:
            try:
                dir_path = os.path.dirname(file_path)
                if dir_path and not os.path.exists(dir_path):
                    os.makedirs(dir_path)
                
                lines = [line] if isinstance(line, str) else line
                
                with open(file_path, 'a', encoding='utf-8') as arquivo:
                    for linha in lines:
                        if not linha.endswith('\n'):
                            linha = linha + '\n'
                        arquivo.write(linha)
                return True
            except Exception as e:
                print(f"Error writing to file {file_path}: {e}")
                return False

    @staticmethod
    def save_message(json_message):
        ''' metodo para salvar uma mensagem em um arquivo txt com o nome do cliente conversado'''
        if not isinstance(json_message, dict):
            print("save_message: json_message não é um dicionário")
            return False

        if "from" not in json_message or "body" not in json_message:
            print("save_message: json_message precisa ter as chaves 'from' e 'body'")
            return False

        sender = str(json_message["from"])
        body = str(json_message["body"])
        date = str(json_message["date"])
        time = str(json_message["time"])

        filename = os.path.join(WriterService.DATA_DIR, "chats", f"{sender}.txt")
        line = f"[{date} - {time}] {sender} : {body}"
        return WriterService._add_line(filename, line)

    @staticmethod
    def save_own_message(json_message):
        ''' precisava-se de um metodo proprio para salvar as proprias mensagens no historico'''
        if not isinstance(json_message, dict):
            print("save_message: json_message não é um dicionário")
            return False

        if "from" not in json_message or "body" not in json_message:
            print("save_message: json_message precisa ter as chaves 'from' e 'body'")
            return False

        sender = str(json_message["from"])
        target = str(json_message["to"])
        body = str(json_message["body"])
        date = str(json_message["date"])
        time = str(json_message["time"])

        filename = os.path.join(WriterService.DATA_DIR, "chats", f"{target}.txt")
        line = f"[{date} - {time}] {sender} : {body}"
        return WriterService._add_line(filename, line)

    ''' metodos para navegacao de path'''
    @staticmethod
    def get_chat_file_path(target):
        return os.path.join(WriterService.DATA_DIR, "chats", f"{target}.txt")
    
    @staticmethod
    def get_user_file_path():
        return os.path.join(WriterService.DATA_DIR, "user.txt")
    
    @staticmethod
    def get_session_file_path(target):
        return os.path.join(WriterService.DATA_DIR, "temp", f"{target}.txt")