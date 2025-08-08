import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding as sym_padding

class AESEncryptor:
    @staticmethod
    def generate_key(key_size: int = 256) -> bytes:
        """
        Gera uma chave AES segura (128, 192 ou 256 bits)
        
        Args:
            key_size: Tamanho da chave em bits (padrão: 256)
            
        Returns:
            bytes: Chave AES em formato binário
            
        Raises:
            ValueError: Se o tamanho for inválido
        """
        valid_sizes = {128, 192, 256}
        if key_size not in valid_sizes:
            raise ValueError(f"Tamanho inválido. Use: {valid_sizes}")
        return os.urandom(key_size // 8)

    @staticmethod
    def generate_iv() -> bytes:
        """Gera um vetor de inicialização (IV) de 16 bytes"""
        return os.urandom(16)

    @staticmethod
    def encrypt(data: bytes, key: bytes, iv: bytes):
        """
        Criptografa dados com AES-CBC (com padding PKCS7)
        
        Args:
            data: Dados a serem criptografados (str ou bytes)
            key: Chave AES (16, 24 ou 32 bytes)
            iv: Vetor de inicialização (opcional)
            
        Returns:
            Tuple[bytes, bytes]: (dados criptografados, IV usado)
        """
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        # Aplica padding PKCS7
        padder = sym_padding.PKCS7(128).padder()
        padded_data = padder.update(data) + padder.finalize()
        
        # Criptografa
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()
        
        return ciphertext

    @staticmethod
    def decrypt(ciphertext: bytes, key: bytes, iv: bytes) -> bytes:
        """
        Descriptografa dados com AES-CBC
        
        Args:
            ciphertext: Dados criptografados
            key: Chave AES usada na criptografia
            iv: Vetor de inicialização usado na criptografia
            
        Returns:
            bytes: Dados originais
        """
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
        decryptor = cipher.decryptor()
        padded_data = decryptor.update(ciphertext) + decryptor.finalize()
        
        # Remove padding
        unpadder = sym_padding.PKCS7(128).unpadder()
        return unpadder.update(padded_data) + unpadder.finalize()
