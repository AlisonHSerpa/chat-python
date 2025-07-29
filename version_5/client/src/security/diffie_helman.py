import base64
import os
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

class Diffie_Helman:
    # Esta classe é responsável por implementar o algoritmo Diffie-Hellman, que permite a troca 
    # segura de chaves criptográficas entre duas partes, para a obtenção de uma chave compartilhada.
    # Também é responsável por gerar o salt, que é usado para derivar a chave compartilhada. 

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
        # A chave compartilhada é derivada usando HKDF, com o Salt, para criar uma chave de 64 bytes.
        derived_key = HKDF(
            algorithm=hashes.SHA256(),
            length=64,
            salt=Salt,
            info=b'handshake data'
        ).derive(shared_key)
        
        # A chave derivada é, então, separada em duas partes: a chave de encriptação e a chave de autenticação.
        encryption_key = derived_key[:32]  # Primeiros 32 bytes para encriptação
        hmac_key = derived_key[32:]  # Últimos 32 bytes para autenticação 
        
        return  encryption_key, hmac_key # Retorna a chave de encriptação, a chave de autenticação  
    
