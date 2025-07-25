import os
from queue import Queue
from threading import Thread

class WriterService:
    def __init__(self):
        self.notification = Queue() # aqui vao ser colocados jsons das mensagens
        self.chat_path = "./chats/"

    def write_file(self, path_file, text, modo='w'):
        ''' escreve algo num diretorio, se nao existir o diretorio ele cria'''
        try:
            # Cria o diretorio se nao existir
            dir_path = os.path.dirname(path_file)
            if dir_path and not os.path.exists(dir_path):
                os.makedirs(dir_path)

            # Escreve no arquivo
            with open(path_file, modo, encoding='utf-8') as arquivo:
                arquivo.write(text)
            return True

        except FileExistsError:
            print(f"Erro: Arquivo '{path_file}' já existe (modo 'x' ativado).")
            return False
        except PermissionError:
            print(f"Erro: Sem permissão para escrever em '{path_file}'.")
            return False
        except IsADirectoryError:
            print(f"Erro: '{path_file}' é um diretório, não um arquivo.")
            return False
        except Exception as e:
            print(f"Erro inesperado ao escrever no arquivo: {e}")
            return False
        
    def read_file(self, path_file, default_content=""):
        """ le um arquivo de texto e entrega tudo que tem nele, se nao existe ele cria """
        try:
            # Try to read the file first
            with open(path_file, 'r', encoding='utf-8') as arquivo:
                return arquivo.read()
                
        except FileNotFoundError:
            try:
                # Create directories if they don't exist
                os.makedirs(os.path.dirname(path_file), exist_ok=True)
                
                # Create file with default content
                with open(path_file, 'w', encoding='utf-8') as arquivo:
                    arquivo.write(default_content)
                return default_content
                
            except Exception as create_error:
                print(f"Erro ao criar arquivo: {create_error}")
                return None
                
        except Exception as read_error:
            print(f"Erro ao ler arquivo: {read_error}")
            return None

    def add_line(self, file_path, line):
        """ Adds a line to a file, creating directories and file if they don't exist """
        try:
            # Create directory if it doesn't exist (using the parent directory of the file)
            dir_path = os.path.dirname(file_path)
            if dir_path:  # Only try to create if there is a directory path
                os.makedirs(dir_path, exist_ok=True)
            
            # Convert single string to list for uniform handling
            lines = [line] if isinstance(line, str) else line
            
            # Open file in append mode (creates file if it doesn't exist)
            with open(file_path, 'a', encoding='utf-8') as arquivo:
                for linha in lines:
                    # Ensure each line ends with newline if it doesn't already
                    if not linha.endswith('\n'):
                        linha = linha + '\n'
                    arquivo.write(linha)
            
            return True
        
        except Exception as e:
            print(f"Error writing to file {file_path}: {e}")
            return False

    def read_notification(self):
        while not self.notification.empty():
            # escreve no historico do chat
            message = self.notification.get()

            # monta o cabecalho da linha
            filename = f"{self.chat_path}{message['from']}.txt"
            line = f"{message['from']} : {message['body']}"

            #escreve a linha
            self.add_line(filename, line)
