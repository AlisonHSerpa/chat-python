from ..security import *
from ..model import HalfKey
from ..model import SessionKey
import base64

class SessionController2:
    
    # diffie helman 1
    # rsa_pub_key precisa estar em pem
    @staticmethod
    def diffie_hellman_1(target : str, pem_rsa_pub_key):
        # Chama uma função para gerar os parãmetros, as chaves pública e privada diffie helman, e o Salt.
        parameters = Diffie_Helman.generate_parameters()
        dh_private_key, dh_public_key = Diffie_Helman.generate_temporary_keys(parameters)
        salt = Diffie_Helman.generate_salt()

        # Os parãmetros e a chave pública dh são transformados em formato PEM para transporte seguro
        pem_public_key = Translate_Pem.chave_para_pem(dh_public_key)
        pem_parameters = Translate_Pem.param_to_pem(parameters)

        # cria e salva metade da chave
        half_key = HalfKey(target, salt, dh_private_key)

        SessionController2.encriptar_chaves_geradas(salt, pem_parameters ,pem_public_key, half_key.target, pem_rsa_pub_key)

    @staticmethod
    def encriptar_chaves_geradas(salt : bytes, pem_parameters, pem_public_key, target, pem_rsa_pub_key):
        from ..service import WriterService
        from ..service import MailService
        from ..model import MessageModel

        # Gera uma chave em formato AES para encriptar todas as informações
        aes_key = AESEncryptor.generate_key() # Gera uma chave AES para encriptar os parâmetros que serão enviados pelo diffie helman
        iv = AESEncryptor.generate_iv() # iv para encriptação aes

        # Encripta as informações (parâmetros, salt e chave pública temporária com a chave AES)
        cript_param = base64.b64encode(AESEncryptor.encrypt(pem_parameters, aes_key, iv)).decode("utf-8")
        cript_salt = base64.b64encode(AESEncryptor.encrypt(salt, aes_key, iv)).decode("utf-8")
        cript_temp_pub = base64.b64encode(AESEncryptor.encrypt(pem_public_key, aes_key, iv)).decode("utf-8")

        # É encriptada a chave AES com a chave RSA (funciona melhor assim, pois a chave AES é pequena o suficiente para ser encriptada pela RSA)
        rsa_pub_key = Translate_Pem.pem_to_chave(pem_rsa_pub_key)
        aes_key_rsa = base64.b64encode(EncryptionRSA.encrypt_with_public_key(aes_key, rsa_pub_key)).decode("utf-8")

        # É também recebido o nome do remetente, para que a mensagem possa ser identificada.
        user = WriterService.read_client()
        origin = user["username"]
        public_key = user["public_key"]

        # Basicamente a chave os parâmetros E O SALT são encriptados com uma chave gerada AES, chave essa que será ser encriptada com a chave RSA.
        # A chave AES, que é encriptada com RSA, é inserida na estrutura da mensagem e enviada junto.
        # A mensagem deve ter a estrutura abaixo

        ''''
        mensagem DH 1
        data = {
            "type" : "DH_1",
            "from" : origin,
            "to" : target,
            "body" : cript_salt,
            "key" : cript_temp_pub,
            "param" : cript_param,
            "aes" : aes_key_rsa,
            "iv" : iv
            "public_key" : public_key,
        }
        '''
        print("DH 1 enviado")
        response = MessageModel("DH_1", origin, target, cript_salt, cript_temp_pub, cript_param, aes_key_rsa, base64.b64encode(iv).decode("utf-8"), public_key)
        print(response.get_message())
        MailService.send_to_mailman(response.get_message())

    # diff hellman 2 comeca aqui, ele recebe a mensagem tipo MessageModel
    @staticmethod
    def diffie_hellman_2(data):
        '''Esse método recebe o body da mensagem com a informação enviada pelo destinatário.
        A chave AES está encriptada com a chave pública RSA do destinatário, então deve ser descriptografada
        com a chave privada RSA do usuário que recebeu a mensagem.
        
        As informações foram encriptadas com a chave AES, quye após ser desencritada, será usada para desencriptar o resto das informações
        '''
        from ..model import MessageModel
        from ..service import WriterService
        from ..service import MailService
        from ..service import SessionKeyService

        try:
            user = WriterService.read_client()
            origin = user["username"]
            rsa_priv_key_user = Translate_Pem.pem_to_chave(user["private_key"])
            target = data["from"]
            cript_salt = base64.b64decode(data["body"])
            cript_temp_pub = base64.b64decode(data["key"])
            cript_param = base64.b64decode(data["param"])
            aes_rsa = base64.b64decode(data["aes"])
            iv = base64.b64decode(data["iv"])
            target_public_key = data["public_key"]

            # Desencripta a chave AES com a chave privada RSA do usuário, garantindo que apenas ele poderá
            aes_DH2 = EncryptionRSA.decrypt_with_private_key(aes_rsa, rsa_priv_key_user)
            print("Chave AES desencriptada!")

            # Após desencriptada, a chave AES pode ser usada pra desencriptar o resto das informações
            param_pem = AESEncryptor.decrypt(cript_param, aes_DH2, iv)
            salt = AESEncryptor.decrypt(cript_salt, aes_DH2, iv)
            chave_dh_pub_pem = AESEncryptor.decrypt(cript_temp_pub, aes_DH2, iv)
            print("Info da mensagem desencriptado com chave AES")

            # Agora que possuímos os parâmetros, faremos as nossas próprias chaves pública e privada dh.
            param = Translate_Pem.pem_to_param(param_pem)
            priv_key_dh2, pub_key_dh2 = Diffie_Helman.generate_temporary_keys(param)
            print("Chaves privada e pública do Diffie Helman 2 criadas!")

            # Com as chaves pública dh1 e privada dh2, poderemos fazer as nossas chaves AES e HMAC.
            pub_key_dh1 = Translate_Pem.pem_to_chave(chave_dh_pub_pem)
            aes_session_DH2, hmac_session_DH2 = Diffie_Helman.exchange_and_derive_key(priv_key_dh2, pub_key_dh1, salt)
            print("Chaves AES e HMAC foram criadas no diffie helman 2!")

            # Aqui ficará o método onde as chaves AES e HMAC temporárias serão armazenadas.
            session_key = SessionKey(target, aes_session_DH2, hmac_session_DH2)
            print(f"SESSION KEY CRIADA: \n {session_key.aes}")

            # Para enviarmos a chave pública DH2, precisaremos antes gerar uma chave AES própria nossa, encriptar a chave pub dh2, e enviar ambas numa mensagem.
            aes_key = AESEncryptor.generate_key()
            iv = AESEncryptor.generate_iv()

            # Traduzimos a chave pub dh2 para formato .pem
            pem_pub_key_dh2 = Translate_Pem.chave_para_pem(pub_key_dh2)

            # Encriptamos a pem pub key dh2 com a chave AES
            cript_temp_pub = base64.b64encode(AESEncryptor.encrypt(pem_pub_key_dh2, aes_key, iv)).decode("utf-8")

            # Encriptamos a chave AES com a chave pública rsa do destinatário.
            peer_public_key = Translate_Pem.pem_to_chave(target_public_key)
            aes_key_rsa = base64.b64encode(EncryptionRSA.encrypt_with_public_key(aes_key, peer_public_key)).decode("utf-8")

            ''''
            mensagem DH 2
            data = {
                "type" : "DH 2",
                "from" : origin,
                "to" : target,
                "body" : "",
                "key" : cript_temp_pub,
                "param" : "",
                "aes" : aes_key_rsa,
                "iv" : iv
            }
            '''

            # monta a mensagem e envia
            response = MessageModel("DH_2", origin, target, "", cript_temp_pub, "", aes_key_rsa, base64.b64encode(iv).decode("utf-8"))
            MailService.send_to_mailman(response.get_message())
            print("Mensagem resposta foi criada!")
            print(response.get_message())
        except Exception as e:
            print(f"Erro ao receber dados [diffie hellman 2]: {e}")

    @staticmethod
    def diffie_hellman_3(data):
        """Completa o handshake DH usando a half key armazenada"""
        from ..service import WriterService
        from ..model import SessionKey
        
        try:
            user = WriterService.read_client()
            current_user = user["username"]
            
            # Verifica se a mensagem é para este usuário
            if data["to"] != current_user:
                print("Mensagem DH_3 não é para este usuário")
                return
                
            private_key = Translate_Pem.pem_to_chave(user["private_key"])
            target = data["from"]  # O remetente é quem enviou DH2
            
            # Processa os dados criptografados
            aes = base64.b64decode(data["aes"])
            iv = base64.b64decode(data["iv"])
            encrypted_dh2_pub = base64.b64decode(data["key"])
            
            # Descriptografa a chave AES
            aes_key = EncryptionRSA.decrypt_with_private_key(aes, private_key)
            dh2_pub_pem = AESEncryptor.decrypt(encrypted_dh2_pub, aes_key, iv)
            
            # Converte para objeto de chave pública
            pub_key_dh2 = Translate_Pem.pem_to_chave(dh2_pub_pem)
            
            # Obtém a half key local (já em formato JSON/dict)
            half_key_data = WriterService.get_half_key(target)
            if not half_key_data:
                raise ValueError(f"Half key para {target} não encontrada")
                
            # Desserializa a chave privada DH1 (retorna PEM bytes + salt)
            dh1_priv_pem, salt = HalfKey.get_data_in_bytes(half_key_data)
            
            # Converte PEM para objeto de chave
            dh1_priv_key = Translate_Pem.pem_to_chave(dh1_priv_pem)
            
            # Deriva as chaves de sessão
            aes_key, hmac_key = Diffie_Helman.exchange_and_derive_key(
                dh1_priv_key, 
                pub_key_dh2, 
                salt
            )
            
            # Armazena a chave de sessão
            session_key = SessionKey(target, aes_key, hmac_key)
            print(f"Session key estabelecida com {target}")
            
            # Limpa a half key após uso (opcional)
            WriterService.insert_half_key("", target, modo="w")
            
        except Exception as e:
            print(f"Erro no DH3: {str(e)}")
            raise