from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import dh
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, dh


class Translate_Pem:

    '''Esta classe é responsável por traduzir chaves entre o formato PEM e os objetos de 
    chave usados pela biblioteca cryptography [CHAVES RSA].
    '''

    '''Esta função é responsável por transformar a chave privada e pública 
    em formato PEM, que é um formato de texto legível por humanos. 
    Ela detecta automaticamente o tipo de chave e a converte para o formato PEM.
    Funciona tanto para chaves RSA quanto para chaves Diffie-Hellman.
    Serve para tornar as chaves portáveis, garantir segurança e facilitar o armazenamento.'''
    @staticmethod
    def chave_para_pem(chave):
        '''Converte a chave para o formato PEM, dependendo se é uma chave privada ou pública.
        Funciona para chaves RSA e Diffie-Hellman.
        
        Args:
            chave: Objeto de chave criptográfica (RSA ou DH)
            
        Returns:
            bytes: Chave no formato PEM
            
        Raises:
            TypeError: Se o tipo de chave não for suportado
        '''
        if isinstance(chave, (rsa.RSAPrivateKey, dh.DHPrivateKey)):
            # Serialização de chave privada
            return chave.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,  # Alterado para PKCS8
                encryption_algorithm=serialization.NoEncryption()
            )
        elif isinstance(chave, (rsa.RSAPublicKey, dh.DHPublicKey)):
            # Serialização de chave pública
            return chave.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
        else:
            raise TypeError(f"Tipo de chave não suportado: {type(chave).__name__}")

    '''# O código abaixo recebe o conteúdo PEM (que já foi lido e inserido em uma variável)
    # e transforma de volta para uma chave privada ou pública. É o processo inverso da função acima.'''
    @staticmethod
    def pem_to_chave(pem_key):
        # Se for string, converte para bytes
        if isinstance(pem_key, str):
            pem_key = pem_key.encode('utf-8')

        if b"PRIVATE KEY" in pem_key:
            return serialization.load_pem_private_key(
                pem_key,
                password=None
            )
        elif b"PUBLIC KEY" in pem_key:
            return serialization.load_pem_public_key(
                pem_key
            )
        else:
            raise ValueError("Chave PEM inválida ou tipo desconhecido")
        

    @staticmethod
    def param_to_pem(parameters):
        # Recebe parâmetros e transforma em um arquivo PEM.
        pem_parameters = parameters.parameter_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.ParameterFormat.PKCS3
        )

        return pem_parameters 
    
    @staticmethod
    def pem_to_param(pem_parameters):
        # Faz o oposto do processo acima
        parameters = serialization.load_pem_parameters(pem_parameters)

        return parameters