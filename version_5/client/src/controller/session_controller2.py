from ..security import*
from ..model import HalfKey
from ..model import SessionKey
import base64

class SessionController2:
    
    # diffie helman 1
    # rsa_pub_key precisa estar em pem
    @staticmethod
    def enviar_um_resquet_dh(target : str , rsa_pub_key):
        # Chama uma função para gerar os parãmetros, as chaves pública e privada diffie helman, e o Salt.
        parameters = Diffie_Helman.generate_parameters()
        dh_private_key, dh_public_key = Diffie_Helman.generate_temporary_keys(parameters)
        salt = Diffie_Helman.generate_salt()

        half_key = HalfKey(target, salt, dh_private_key)

        # Os parãmetros e a chave pública dh são transformados em formato PEM para transporte seguro
        pem_public_key = Translate_Pem.chave_para_pem(dh_public_key)
        pem_parameters = Translate_Pem.param_to_pem(parameters)

        SessionController2.encriptar_chaves_geradas(salt, pem_parameters ,pem_public_key, half_key, rsa_pub_key)

    @staticmethod
    def encriptar_chaves_geradas(salt : bytes, pem_parameters, pem_public_key, half_key, rsa_pub_key):
        from ..model import MessageDH
        from ..service import WriterService
        from ..service import MailService

        param64, salt64, key64 = SessionController2._passar_para_b64(pem_parameters, salt, pem_public_key)

        # Logo após, a mensagem deve ser encriptada com a chave pública rsa do destinatário.
        cript_param64 = EncryptionRSA.encrypt_with_public_key(param64, rsa_pub_key)
        cript_salt64 = EncryptionRSA.encrypt_with_public_key(salt64, rsa_pub_key)
        cript_key64 = EncryptionRSA.encrypt_with_public_key(key64, rsa_pub_key)

        # Após a mensagem ser encriptada, ela deve ser novamente encodada em base64 e utf-8, 
        # para poder ser inserida no json da mensagem.
        b64cript_param64 = base64.b64encode(cript_param64).decode('utf-8') 
        b64cript_salt64 = base64.b64encode(cript_salt64).decode('utf-8') 
        b64cript_key64 = base64.b64encode(cript_key64).decode('utf-8') 

        # É também recebido o nome do remetente, para que a mensagem possa ser identificada.
        user = WriterService.read_client()
        origin_name = user["username"]

        # Cria a mensagem com o tipo "session_key" e envia para o destinatário.
        # A mensagem é criada com o nome do remetente, o nome do destinatário e o corpo da mensagem.
        # O destino é o usuário com quem a sessão está sendo estabelecida, que irá receber os 
        # parâmetros e o salt.
        final_message = MessageDH("session_key", origin_name, half_key["usuario_alvo"], b64cript_param64, b64cript_salt64, b64cript_key64)
        MailService.send_to_mailman(final_message.get_message().encode())

    # diff hellman 2 comeca aqui, ele recebe a mensagem tipo MessageDH
    @staticmethod
    def separar_dados_dh(data):
        '''Esse método recebe o body da mensagem com a informação enviada pelo destinatário.
        A informação está encriptada com a chave pública do destinatário, então deve ser descriptografada
        com a chave privada do usuário.'''
        from ..model import MessageModel
        from ..service import WriterService
        from ..service import MailService
        from ..service import SessionKeyService

        try:
            user = WriterService.read_client()

            # Descriptografa os dados usando a chave privada do usuário
            parametros_b64 = EncryptionRSA.decrypt_with_private_key(data["parametros"]).decode('utf-8')
            salt_b64 = EncryptionRSA.decrypt_with_private_key(data["salt"]).decode('utf-8')
            key_b64 = EncryptionRSA.decrypt_with_private_key(data["key"]).decode('utf-8')

            # Depois de separar, as variáveis são re-codificadas para bytes.
            parametros = base64.b64decode(parametros_b64)
            salt = base64.b64decode(salt_b64)
            chave_publica = base64.b64decode(key_b64)

            # depois
            pem_public_key = SessionKey(data["from"], parametros, salt, chave_publica)
            dh_public_key = pem_public_key.primeiro_aes_e_hmac() # ta em bytes

            # faz ser serializavel
            b64_dh_response_public_key = base64.b64encode(dh_public_key).decode('utf-8')

            # pega a publica do cara
            peer_public_key = SessionKeyService.verificar_rsa_pub_key(user["username"], data["from"])

            b64_dh_response_public_key_encrypted = EncryptionRSA.encrypt_with_public_key(b64_dh_response_public_key, peer_public_key)

            response = MessageModel("session_key_response",user["username"], data["from"], b64_dh_response_public_key_encrypted)
            MailService.send_to_mailman(response.get_message().encode())

        except Exception as e:
            print(f"Erro ao receber dados (separar_dados_dh): {e}")

    @staticmethod
    def completar_session_key(target, b64_dh_response_public_key_encrypted):
        from ..service import WriterService
        data = WriterService.read_client()

        # desencripta com a chave privada
        b64_dh_response_public_key  =EncryptionRSA.decrypt_with_private_key(b64_dh_response_public_key_encrypted, data["private_key"])

        # tira a resposta da base64 para bytes
        chave_publica_resposta = base64.b64decode(b64_dh_response_public_key)

        # recolhe de volta os dados da chave
        half_key_data = WriterService.get_half_key(target)
        dh_private_key , salt = HalfKey.get_data_in_bytes(half_key_data)

        # faz a sua session key
        session_key = SessionKey(target)
        session_key.segunda_aes_e_hmac(chave_publica_resposta, dh_private_key, salt)

    ''' metodo auxiliar '''
    @staticmethod
    def _passar_para_b64(pem_parameters: bytes, salt: bytes, pem_public_key: bytes):
        # Codifica os dados em base64 para enviar via socket
        parametros_b64 = base64.b64encode(pem_parameters).decode('utf-8')
        salt_b64 = base64.b64encode(salt).decode('utf-8')
        chave_publica_b64 = base64.b64encode(pem_public_key).decode('utf-8')


        # Codifica a string final em bytes
        return parametros_b64 , salt_b64, chave_publica_b64