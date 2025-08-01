# version_5/client/src/controller/session_controller.py
from ..service import WriterService
from ..model import SessionKey
from ..model import MessageModel
from ..security import *
import base64

class SessionController:

    '''Classe responsável por receber informação do body da mensagem que contém a chave pública do destinatário,
    o salt e os parâmetros necessários para a realização do Diffie-Hellman.'''


    '''A classe espera que os dados no Body, caso sejam os 3, sejam separados por "<SEP>", 
    e enviados na ordem ["parâmetros", "salt", "chave_pública"].'''
    @staticmethod
    def separar_dados_dh(body: bytes, sender_name: str):
        '''Esse método recebe o body da mensagem com a informação enviada pelo destinatário.
        A informação está encriptada com a chave pública do destinatário, então deve ser descriptografada
        com a chave privada do usuário.'''
        
        encrypted_data = body

        '''A chave privada do usuário é lida do arquivo user.txt.
        Ela é armazenada em formato PEM, então deve ser convertida para bytes'''
        
        dados_cliente = WriterService.read_client()
        
        chave_privada = dados_cliente["private_key"].encode('utf-8') # A chave privada é extraída do json e
        # re-codificada para bytes.
        
        try:
            # Descriptografa os dados usando a chave privada do usuário
            decrypted_data = EncryptionRSA.decrypt_with_private_key(chave_privada, encrypted_data)
            # Decodifica os dados de volta para string e separa os componentes
            # usando o separador "<SEP>".
            data = decrypted_data.decode('utf-8')

            # Verifica se os dados contêm o separador "<SEP>". Caso contrário, significa 
            # que o remetente enviou apenas a chave pública. 
            if "<SEP>" in data:
                # Separa os dados usando o separador "<SEP>"
                parametros_b64, salt_b64, chave_publica_b64 = data.split("<SEP>")
                # Depois de separar, as variáveis são re-codificadas para bytes.
                parametros = base64.b64decode(parametros_b64)
                salt = base64.b64decode(salt_b64)
                chave_publica = base64.b64decode(chave_publica_b64)
            else:
                # Se não houver separador, assume que o remetente enviou apenas a chave pública
                chave_publica_b64 = data
                chave_publica = base64.b64decode(chave_publica_b64)
                # Define os parâmetros e o salt como None, indicando para o SessionKey que não é 
                # necessário sobescrever os valores.
                parametros = None
                salt = None
            # Armazena os dados no SessionKey
            pem_public_key = SessionKey.set_session_key(parametros, salt, chave_publica)

            if pem_public_key is not None:
                # Retorna a chave pública para o destinatário feita com os parâmetros gerados pelo mesmo.
                return SessionController.enviar_chave_publica(None, None, pem_public_key, sender_name)
            
 
        except Exception as e:
            print(f"Erro ao receber dados (separar_dados_dh): {e}")
    
    @staticmethod
    def preparar_envio(parameters: bytes, salt: bytes, pem_public_key: bytes):
        # Codifica os dados em base64 para enviar via socket
        parametros_b64 = base64.b64encode(parameters) 
        salt_b64 = base64.b64encode(salt)
        chave_publica_b64 = base64.b64encode(pem_public_key)

        # Junta os dados com o separador "<SEP>"
        data = f"{parametros_b64}<SEP>{salt_b64}<SEP>{chave_publica_b64}"
        # Codifica a string final em bytes
        return data.encode('utf-8')



    '''Este método é responsável por enviar a chave pública do usuário em formato pem (e os parâmetros e o Salt)
    para o destinatário. Ele deve ser chamado após o usuário ter gerado suas chaves e iniciado a 
    sessão, OU após receber os parâmetros e o Salt do destinatário.'''

    @staticmethod
    def enviar_chave_publica(parameters: bytes, salt: bytes, pem_public_key: bytes, destiny_name: str):
        # destiny_name é o nome do destinatário, que é o usuário com quem a sessão está sendo estabelecida.
        if not parameters and not salt:
            print("Parâmetros ou salt não fornecidos, será enviada apenas a chave pública.")
             
            b64_public_key =  base64.b64encode(pem_public_key)

            mensagem = b64_public_key.encode('utf-8')

            # TODO: Ainda não há implementação para armazenar a chave pública do destinatário.
            peer_public_key = None  # Deve ser substituído pela chave pública do destinatário.

            # Encripta a mensagem com a chave pública do destinatário
            mensagem_encriptada = EncryptionRSA.encrypt_with_public_key(mensagem, peer_public_key)

            # Após a mensagem ser encriptada, ela deve ser novamente encodada em base64 e utf-8, 
            # para poder ser inserida no json da mensagem.
            mensagem_encodada = base64.b64encode(mensagem_encriptada).decode('utf-8') 

            # É também recebido o nome do remetente, para que a mensagem possa ser identificada.
            user = WriterService.read_client()
            origin_name = user["username"]

            # Cria a mensagem com o tipo "session_key_response" e envia para o destinatário.
            # A mensagem é criada com o nome do remetente, o nome do destinatário e o corpo da mensagem.
            # O destino é o usuário com quem a sessão está sendo estabelecida, que primeiramente enviou os 
            # parâmetros e o salt.
            final_message = MessageModel("session_key_response", origin_name, destiny_name, mensagem_encodada)

            # Retorna a mensagem para o client_controller, que irá enviar via socket.
            return final_message


        elif parameters is not None and salt is not None and pem_public_key is not None:
            # Prepara os dados para envio, codificando em base64, depois juntando com o separador "<SEP>"
            # e, por fim, convertendo para string.
            mensagem = SessionController.preparar_envio(parameters, salt, pem_public_key)

            # Logo após, a mensagem deve ser encriptada com a chave pública rsa do destinatário.
            # TODO: Ainda não há implementação para armazenar a chave pública do destinatário.
            peer_public_key = None  # Deve ser substituído pela chave pública do destinatário.
            
            # Envia os dados para o destinatário via socket
            mensagem_encriptada = EncryptionRSA.encrypt_with_public_key(mensagem, peer_public_key)

        '''
            recebe uma rsa_pub_key e começa o DH (gera parametros, salt e as 2 chaves DH)
            retorna uma mensagem do tipo session key (salt, pub_key_DH, parametros) para o mailman
        '''