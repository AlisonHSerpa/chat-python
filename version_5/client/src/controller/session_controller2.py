from ..security import *
from ..model import HalfKey
from ..model import SessionKey
import base64

class SessionController2:
    
    # diffie helman 1
    # rsa_pub_key precisa estar em pem
    @staticmethod
    def enviar_um_request_dh(target : str, rsa_pub_key):
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
        from ..service import WriterService
        from ..service import MailService

        # Gera uma chave em formato AES para encriptar todas as informações
        aes_key = AESEncryptor.generate_key() # Gera uma chave AES para encriptar os parâmetros que serão enviados pelo diffie helman
        iv = AESEncryptor.generate_iv() # iv para encriptação aes

        # Encripta as informações (parâmetros, salt e chave pública temporária com a chave AES)
        cript_param = AESEncryptor.encrypt(pem_parameters, aes_key, iv)
        cript_salt = AESEncryptor.encrypt(salt, aes_key, iv)
        cript_temp_pub = AESEncryptor.encrypt(pem_public_key, aes_key, iv)

        # É encriptada a chave AES com a chave RSA (funciona melhor assim, pois a chave AES é pequena o suficiente para ser encriptada pela RSA)
        aes_key_rsa = EncryptionRSA.encrypt_with_public_key(aes_key, rsa_pub_key)

        # É também recebido o nome do remetente, para que a mensagem possa ser identificada.
        user = WriterService.read_client()
        origin_name = user["username"]

        # Basicamente a chave os parâmetros E O SALT são encriptados com uma chave gerada AES, chave essa que será ser encriptada com a chave RSA.
        # A chave AES, que é encriptada com RSA, é inserida na estrutura da mensagem e enviada junto.
        # A mensagem deve ter a estrutura abaixo
        
        data = {
            "param" : cript_param,
            "salt" : cript_salt,
            "key" : cript_temp_pub,
            "aes" : aes_key_rsa,
            "iv" : iv
        }
        
        MailService.send_to_mailman(data.encode())

    # diff hellman 2 comeca aqui, ele recebe a mensagem tipo MessageDH
    @staticmethod
    def separar_dados_dh(data):
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

            # Desencripta a chave AES com a chave privada RSA do usuário, garantindo que apenas ele poderádata
            aes_DH2 = EncryptionRSA.decrypt_with_private_key(data["aes"])
            print("Chave AES desencriptada!")

            # Após desencriptada, a chave AES pode ser usada pra desencriptar o resto das informações
            param_pem = AESEncryptor.decrypt(data["param"], aes_DH2, data["iv"])
            salt = AESEncryptor.decrypt(data["salt"], aes_DH2, data["iv"])
            chave_dh_pub_pem = AESEncryptor.decrypt(data["key"], aes_DH2, data["iv"])
            print("Info da mensagem desencriptado com chave AES")

            # Agora que possuímos os parâmetros, faremos as nossas próprias chaves pública e privada dh.
            param = Translate_Pem.pem_to_param(param_pem)
            priv_key_dh2, pub_key_dh2 = Diffie_Helman.generate_temporary_keys(param)
            print("Chaves privada e pública do Diffie Helman 2 criadas!")

            # Com as chaves pública dh1 e privada dh2, poderemos fazer as nossas chaves AES e HMAC.
            pub_key_dh1 = Translate_Pem.receive_key(chave_dh_pub_pem)
            aes_session_DH2, hmac_session_DH2 = Diffie_Helman.exchange_and_derive_key(priv_key_dh2, pub_key_dh1, salt)
            print("Chaves AES e HMAC foram criadas no diffie helman 2!")

            # Aqui ficará o método onde as chaves AES e HMAC temporárias serão armazenadas.


            # Para enviarmos a chave pública DH2, precisaremos antes gerar uma chave AES própria nossa, encriptar a chave pub dh2, e enviar ambas numa mensagem.
            aes_key = AESEncryptor.generate_key()
            iv = AESEncryptor.generate_iv()

            # Traduzimos a chave pub dh2 para formato .pem
            pem_pub_key_dh2 = Translate_Pem.chave_para_pem(pub_key_dh2)

            # Encriptamos a pem pub key dh2 com a chave AES
            cript_temp_pub = AESEncryptor.encrypt(pem_pub_key_dh2, aes_key, iv)

            # Encriptamos a chave AES com a chave pública rsa do destinatário.
            peer_public_key = SessionKeyService.verificar_rsa_pub_key(user["username"], data["from"])
            aes_key_rsa = EncryptionRSA.encrypt_with_public_key(aes_key, peer_public_key)

            response = {
            "key" : cript_temp_pub,
            "aes" : aes_key_rsa,
            "iv" : iv
            }

            MailService.send_to_mailman(response.encode())
            print("Mensagem resposta foi criada!")
        except Exception as e:
            print(f"Erro ao receber dados (separar_dados_dh): {e}")

    @staticmethod
    def completar_session_key(target, aes, key, iv):
        # A função recebe a chave aes, a chave pública dh2 e o iv da mensagem para serem desencriptados e usados para o diffie helman 3.
        from ..service import WriterService
        data = WriterService.read_client()

        # Extraímos a chave AES e desencriptamos ela com nossa chave RSA privada.
        aes_DH2 = EncryptionRSA.decrypt_with_private_key(aes)
        temp_pub_pem = AESEncryptor.decrypt(key, aes_DH2, iv)
        print('Chave AES foi desencriptada no diffie helman 3!')

        pub_key_dh2 = Translate_Pem.pem_to_chave(temp_pub_pem)
        
        # recolhe de volta os dados da chave
        half_key_data = WriterService.get_half_key(target)
        priv_key_dh1, salt = HalfKey.get_data_in_bytes(half_key_data)

        # faz a sua session key
        aes_dh3, hmac_dh3 = Diffie_Helman.exchange_and_derive_key(priv_key_dh1, pub_key_dh2, salt)
        print("Chaves AES e HMAC foram geradas no diffie helman 3!")

        # Aqui será o método que irá armazenar as chaves AES e HMAC.




    ''' metodo auxiliar '''
    @staticmethod
    def _passar_para_b64(pem_parameters: bytes, salt: bytes, pem_public_key: bytes):
        # Codifica os dados em base64 para enviar via socket
        parametros_b64 = base64.b64encode(pem_parameters).decode('utf-8')
        salt_b64 = base64.b64encode(salt).decode('utf-8')
        chave_publica_b64 = base64.b64encode(pem_public_key).decode('utf-8')


        # Codifica a string final em bytes
        return parametros_b64 , salt_b64, chave_publica_b64