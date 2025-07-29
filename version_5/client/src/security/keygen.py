# Este arquivo serve para armazenar as funções de criação de senhas que serão implementadas na criação de perfis.

# Os imports abaixo trazem as funções de derivação de chave, diffie-helman e parãmetros.

import os
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.asymmetric import dh
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import load_pem_parameters
import base64

class Keygen:

    # Esta classe é dividida em seções, onde cada uma é separada de acordo com a parte de qual participa. 
    # Seja a criação das chaves rsa, a criação das chaves diffie-helman, a encriptação e descriptografia de mensagens,
    # a geração de salt, ou o Diffie-Hellman em si. Ela também é responsável por transformar e ler objetos de chave em 
    # formato PEM, que pode ser usado para armazenar chaves de forma segura e portátil.
    

    # Esta função é responsável por transformar a chave privada e pública 
    # em formato PEM, que é um formato de texto legível por humanos. 
    # Ela detecta automaticamente o tipo de chave e a converte para o formato PEM.
    # Funciona tanto para chaves RSA quanto para chaves Diffie-Hellman.
    # Serve para tornar as chaves portáveis, garantir segurança e facilitar o armazenamento.
    @staticmethod
    def rsa_chave_para_pem(chave):
        if isinstance(chave, rsa.RSAPrivateKey): # Chave privada RSA
            return chave.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()
            )
        elif isinstance(chave, rsa.RSAPublicKey): # Chave pública RSA
            return chave.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
        elif isinstance(chave, dh.DHPrivateKey): # Chave privada Diffie-Hellman
            return chave.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()
            )
        elif isinstance(chave, dh.DHPublicKey): # Chave pública Diffie-Hellman
            return chave.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
        else:
            raise TypeError("Tipo de chave não suportado")

    # O código abaixo recebe o conteúdo PEM (que já foi lido e inserido em uma variável)
    # e transforma de volta para uma chave privada ou pública. É o processo inverso da função acima.
    @staticmethod
    def receive_key(pem_key):
        if isinstance(pem_key, dh.DHPrivateKey):
            # Se a chave for uma chave privada do Diffie-Hellman, ela é carregada diretamente.
            return serialization.load_pem_private_key(
                pem_key,
                password=None
            )
        elif isinstance(pem_key, dh.DHPublicKey):
            # Se a chave for uma chave pública do Diffie-Hellman, ela é carregada diretamente.
            return serialization.load_pem_public_key(
                pem_key
            )
        elif isinstance(pem_key, rsa.RSAPrivateKey):
            # Se a chave for uma chave privada RSA, ela é carregada diretamente.
            return serialization.load_pem_private_key(
                pem_key,
                password=None
            )
        elif isinstance(pem_key, rsa.RSAPublicKey):
            # Se a chave for uma chave pública RSA, ela é carregada diretamente.
            return serialization.load_pem_public_key(
                pem_key
            )
        else:
            raise TypeError("Tipo de chave não suportado")
   
   
    # O código abaixo gera as chave privada e pública PERSISTENTES (RSA) que serão usadas para o diffie-helman posteriormente.
    @staticmethod
    def generate_rsa_keys():
        private_key = rsa.generate_private_key(65537, 2048) # Expoente é um número primo que é usado para o cálculo, 2048 é o tamanho da chave criada
        public_key = private_key.public_key()

        # As chaves são convertida para o formato PEM, que é um formato de texto legível por humanos.
        pem_priv = Keygen.rsa_chave_para_pem(private_key)
        
        pem_pub = Keygen.rsa_chave_para_pem(public_key)

        # As chaves são retornadas em formato PEM para serem armazenadas em um arquivo PEM. 
        return pem_priv, pem_pub
    
   
    # Este método recebe uma chave pública do destinatário e a usa encriptar dados. É usado no Diffie-Hellman para enviar os 
    # dados que resultam na chave compartilhada. Como a chave é armazenada em formato PEM, ela é convertida para o objeto de chave pública.
    @staticmethod
    def encrypt_with_public_key(pem_peer_public_key, message):

        # A chave pública é carregada a partir do conteúdo PEM.
        peer_public_key = Keygen.receive_key(pem_peer_public_key)
        
        # A mensagem é encriptada com a chave pública do destinatário.
        ciphertext = peer_public_key.encrypt(
            message,
            padding=serialization.OAEP(
                mgf=serialization.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return ciphertext

    # Este método recebe uma chave privada do usuário e a usa para descriptografar dados. É usado no Diffie-Hellman. 
    # A chave privada é recebida em formato PEM e convertida para o objeto de chave privada. 
    @staticmethod
    def decrypt_with_private_key(pem_private_key, ciphertext):
        # A chave privada é carregada a partir do conteúdo PEM.
        private_key = Keygen.receive_private_key(pem_private_key)
        # A mensagem é descriptografada com a chave privada do usuário.
        plaintext = private_key.decrypt(
            ciphertext,
            padding=serialization.OAEP(
                mgf=serialization.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return plaintext
   
    # O código abaixo lê o arquivo de parâmetros para a geração de chaves.
    # Os parãmetros são usados para o Diffie-Hellman, que é um protocolo de troca de chaves.
    # O arquivo de parâmetros deve ser gerado previamente e armazenado no diretório especificado.
    # Os parâmetros são sempre 2 e 2048, mas eles sempre serão gerados por quem iniciou a sessão.
    @staticmethod
    def get_parameters():
        with open("version_5/client/src/security/dh_params.pem", "rb") as f:
            parameters = load_pem_parameters(f.read())
        return parameters
    
    # O código abaixo gera uma chave privada e pública temporária para o Diffie-Hellman.
    # A chave privada é gerada a partir dos parâmetros lidos do arquivo e 
    # a chave pública é gerada a partir da chave privada. 
    # A chave privada é inserida na função Diffie-Helman e a pública é enviada para o destinatário via socket.
    @staticmethod
    def generate_temporary_keys():
        parameters = Keygen.get_parameters()
        private_key = dh.generate_private_key(parameters)
        public_key = private_key.public_key()

        return private_key, public_key

    # O salt é gerado aleatoriamente para ser usado na derivação da chave compartilhada.
    # Ele deve ser único para cada sessão de Diffie-Hellman.
    # O salt é usado para derivar a chave compartilhada e deve ser armazenado junto com a chave compartilhada.
    # O salt é enviado junto com a chave pública do destinatário para que ele possa derivar a mesma chave compartilhada.
    def generate_salt():
        return base64.urlsafe_b64encode(os.urandom(16))

    # Este método é o Diffie-Hellman em si. Ele recebe um valor segredo do destinatário e, junto com uma valor segredo 
    # privado gera uma chave compartilhada.
    # O Diffie-Helman deve ser usado em conjunto com a encriptação das chaves públicas e privadas, que são usadas para trocar 
    # dados de forma segura.
    # O método recebe tanto as chaves quanto o Salt, que é usado para derivar a chave compartilhada.
    @staticmethod
    def diffie_Helman(temp_private_key, temp_peer_public_key, Salt):
        # A chave compartilhada é gerada a partir da chave privada do usuário e da chave pública do destinatário.
        shared_key = temp_private_key.exchange(temp_peer_public_key)
        # A chave compartilhada é derivada usando HKDF para criar uma chave de 32 bytes.
        derived_key = HKDF(
            algorithm=hashes.SHA256(),
            length=64,
            salt=Salt,
            info=b'handshake data'
        ).derive(shared_key)
        return derived_key
    