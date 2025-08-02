import os
from cryptography.hazmat.primitives.serialization import load_pem_parameters
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.asymmetric import dh
class Diffie_Helman:
    ''' Esta classe é responsável por implementar o algoritmo Diffie-Hellman, que permite a troca 
    segura de chaves criptográficas entre duas partes, para a obtenção de uma chave compartilhada.
    Também é responsável por gerar o salt, que é usado para derivar a chave compartilhada.''' 
    
    '''O código abaixo gera parâmetros para a geração de chaves.
    Os parãmetros são usados para o Diffie-Hellman, que é um protocolo de troca de chaves.
    Os parâmetros devem ser gerados previamente e enviados após o uso para a criação de chaves dh.
    Os parâmetros são sempre 2 e 2048, mas eles sempre serão gerados por quem iniciou a sessão.'''
    @staticmethod
    def generate_parameters():
        parameters = dh.generate_parameters(
            generator=2, key_size=2048
        )
        return parameters
    
    '''O código abaixo gera uma chave privada e pública temporária para o Diffie-Hellman.
    A chave privada é gerada a partir dos parâmetros lidos do arquivo e 
    a chave pública é gerada a partir da chave privada. 
    A chave privada é inserida na função Diffie-Helman e a pública é enviada para o destinatário via socket.'''
    @staticmethod
    def generate_temporary_keys(parameters):
        private_key = parameters.generate_private_key() # Gera a chave privada temporária
        public_key = private_key.public_key() # Gera a chave pública temporária

        return private_key, public_key
    
    '''O salt é gerado aleatoriamente para ser usado na derivação da chave compartilhada.
    Ele deve ser único para cada sessão de Diffie-Hellman.
    O salt é usado para derivar a chave compartilhada e deve ser armazenado junto com a chave compartilhada.
    O salt é enviado junto com a chave pública do destinatário para que ele possa derivar a mesma chave compartilhada.'''
    @staticmethod
    def generate_salt():
        return os.urandom(16)

    '''Este método é o Diffie-Hellman em si. Ele recebe um valor segredo do destinatário e, junto com uma valor segredo 
    privado gera uma chave compartilhada.
    O Diffie-Helman deve ser usado em conjunto com a encriptação das chaves públicas e privadas, que são usadas para trocar 
    dados de forma segura.
    O método recebe tanto as chaves quanto o Salt, que é usado para derivar a chave compartilhada.'''
    @staticmethod
    def exchange_and_derive_key(temp_private_key: bytes, temp_peer_public_key: bytes, Salt: bytes):
        # A chave compartilhada é gerada a partir da chave privada do usuário e da chave pública do destinatário.
        shared_key = temp_private_key.exchange(temp_peer_public_key)
        # A chave compartilhada é derivada usando HKDF, com o Salt, para criar uma chave de 64 bytes.
        derived_key = HKDF(
            algorithm=hashes.SHA256(),
            length=64,
            salt=Salt,
            info=b'handshake data'
        ).derive(shared_key)
        
        # A chave derivada é, então, separada em duas partes: a chave de encriptação e a chave de autenticação.
        aes_key = derived_key[:32]  # Primeiros 32 bytes para encriptação
        hmac_key = derived_key[32:]  # Últimos 32 bytes para autenticação 
        
        return  aes_key, hmac_key # Retorna a chave de encriptação, a chave de autenticação  
    
'''
# -------------------------------------------------------
# TESTE AUTOMÁTICO AO EXECUTAR DIRETAMENTE O SCRIPT
# -------------------------------------------------------

if __name__ == "__main__":
    print("[*] Iniciando teste de troca de chaves Diffie-Hellman...")

    # Geração de parâmetros e chaves
    params = Diffie_Helman.generate_parameters()
    priv1, pub1 = Diffie_Helman.generate_temporary_keys(params)
    priv2, pub2 = Diffie_Helman.generate_temporary_keys(params)
    salt = Diffie_Helman.generate_salt()

    # Derivação dos dois lados
    aes1, hmac1 = Diffie_Helman.exchange_and_derive_key(priv1, pub2, salt)
    aes2, hmac2 = Diffie_Helman.exchange_and_derive_key(priv2, pub1, salt)

    # Verificações
    assert aes1 == aes2, "Erro: AES keys diferentes!"
    assert hmac1 == hmac2, "Erro: HMAC keys diferentes!"

    print("[✔] Chaves derivadas coincidem. Teste concluído com sucesso.")
#'''