from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import dh


class Translate_Pem:

    # Esta classe é responsável por traduzir chaves entre o formato PEM e os objetos de 
    # chave usados pela biblioteca cryptography.


    # Esta função é responsável por transformar a chave privada e pública 
    # em formato PEM, que é um formato de texto legível por humanos. 
    # Ela detecta automaticamente o tipo de chave e a converte para o formato PEM.
    # Funciona tanto para chaves RSA quanto para chaves Diffie-Hellman.
    # Serve para tornar as chaves portáveis, garantir segurança e facilitar o armazenamento.
    @staticmethod
    def chave_para_pem(chave):
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