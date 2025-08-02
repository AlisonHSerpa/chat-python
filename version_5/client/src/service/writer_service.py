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
            raise ValueError("[read_client] erro ao tentar ler usuario")

        file_lock = WriterService._get_file_lock(diretorio)
        with file_lock:
            try:
                with open(diretorio, "w", encoding="utf-8") as f:
                    json.dump(json_data, f, indent=4)
            except Exception as e:
                raise RuntimeError(f"[write_client] Erro ao escrever o arquivo JSON: {e}")

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
                raise FileNotFoundError(f"[read_client] Arquivo '{diretorio}' não encontrado.")
            except json.JSONDecodeError:
                raise ValueError(f"[read_client] O conteúdo do arquivo '{diretorio}' não é um JSON válido.")
            except Exception as e:
                raise RuntimeError(f"[read_client] Erro ao ler arquivo JSON: {e}")


    @staticmethod
    def insert_session_key(json_session_key: str, username: str, path_file=None, modo='w'):
        '''Salva a session key em arquivo — aceita apenas JSON string'''
        if path_file is None:
            path_file = WriterService.get_session_file_path(username)

        file_lock = WriterService._get_file_lock(path_file)

        with file_lock:
            try:
                # Valida se a string é um JSON válido antes de salvar
                json.loads(json_session_key)

                dir_path = os.path.dirname(path_file)
                if dir_path and not os.path.exists(dir_path):
                    os.makedirs(dir_path)

                with open(path_file, modo, encoding='utf-8') as arquivo:
                    arquivo.write(json_session_key)

                return True
            except json.JSONDecodeError:
                print("[write_session_key] Erro: JSON inválido fornecido.")
                return False
            except Exception as e:
                print(f"[write_session_key] Erro ao escrever no arquivo: {e}")
                return False

    @staticmethod
    def get_session_key(username: str):
        '''Lê a session key do disco e retorna como string JSON'''
        path = WriterService.get_session_file_path(username)

        if not os.path.exists(path):
            return None

        file_lock = WriterService._get_file_lock(path)

        with file_lock:
            try:
                with open(path, 'r', encoding='utf-8') as file:
                    return file.read()  # retorna string JSON
            except Exception as e:
                print(f"[get_session_key] Erro: {e}")
                return None
            
    @staticmethod
    def insert_half_key(half_key_data: str, username : str, path_file=None, modo='w'):
        '''Salva a half key em arquivo — aceita apenas JSON string'''
        if path_file is None:
            path_file = WriterService.get_half_key_file_path(username)

        file_lock = WriterService._get_file_lock(path_file)

        with file_lock:
            try:
                # Valida se a string é um JSON válido antes de salvar
                json.loads(half_key_data)

                dir_path = os.path.dirname(path_file)
                if dir_path and not os.path.exists(dir_path):
                    os.makedirs(dir_path)

                with open(path_file, modo, encoding='utf-8') as arquivo:
                    arquivo.write(half_key_data)

                return True
            except json.JSONDecodeError:
                print("[insert_half_key] Erro: JSON inválido fornecido.")
                return False
            except Exception as e:
                print(f"[insert_half_key] Erro ao escrever no arquivo: {e}")
                return False

    @staticmethod     
    def get_half_key(username):
        '''Procura e lê a half key e retorna como string JSON'''
        path = WriterService.get_half_key_file_path(username)

        if not os.path.exists(path):
            return None

        file_lock = WriterService._get_file_lock(path)

        with file_lock:
            try:
                with open(path, 'r', encoding='utf-8') as file:
                    return file.read()  # retorna string JSON
            except Exception as e:
                print(f"[get_half_key] Erro: {e}")
                return None

    @staticmethod
    def read_chat_history(path_file, default_content=""):
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
                print(f"[read_chat_history] Erro ao ler/criar arquivo: {e}")
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
                print(f"[add_line] Error writing to file {file_path}: {e}")
                return False

    @staticmethod
    def save_message(json_message):
        ''' Salva uma mensagem recebida no arquivo do remetente '''
        if isinstance(json_message, str):
            try:
                json_message = json.loads(json_message)
            except json.JSONDecodeError as e:
                print(f"[save_message] erro ao decodificar JSON: {e}")
                return False

        if not isinstance(json_message, dict):
            print("[save_message] json_message não é um dicionário")
            return False

        required_keys = {"type", "from", "to", "body", "date", "time"}
        if not required_keys.issubset(json_message.keys()):
            print("[save_message] json_message está faltando campos obrigatórios")
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
        ''' Salva uma mensagem enviada no arquivo do destinatário '''
        if isinstance(json_message, str):
            try:
                json_message = json.loads(json_message)
            except json.JSONDecodeError as e:
                print(f"[save_own_message] erro ao decodificar JSON: {e}")
                return False

        if not isinstance(json_message, dict):
            print("[save_own_message] json_message não é um dicionário")
            return False

        required_keys = {"type", "from", "to", "body", "date", "time"}
        if not required_keys.issubset(json_message.keys()):
            print("[save_own_message] json_message está faltando campos obrigatórios")
            print(json_message)
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
        return os.path.join(WriterService.DATA_DIR, "sessionkey", f"{target}.txt")
    
    @staticmethod
    def get_half_key_file_path(target):
        return os.path.join(WriterService.DATA_DIR, "halfkey", f"{target}.txt")
    
'''
if __name__ == "__main__":
    import json
    from datetime import datetime

    # Simula uma session key em formato JSON
    session_data = {
        "username": "alice",
        "peer_username": "bob",
        "aes_key": "YmFzZTY0LWFlcy1rZXk=",  # exemplo base64
        "hmac_key": "aG1hYy1rZXk=",           # exemplo base64
        "creation_time": datetime.now().strftime("%H:%M"),
        "expiration_seconds": 3600,
        "remaining_messages": 100,
        "valid": True
    }

    json_str = json.dumps(session_data, indent=2)

    print("===> Salvando session key...")
    sucesso = WriterService.write_session_key(json_str, "bob")

    if sucesso:
        print("Session key salva com sucesso!\n")
    else:
        print("Falha ao salvar session key.\n")

    print("===> Lendo session key...")
    resultado = WriterService.get_session_key("bob")

    if resultado:
        print("Session key lida com sucesso:")
        print(resultado)
    else:
        print("Session key não encontrada ou erro ao ler.")

#'''