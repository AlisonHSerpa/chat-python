from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

class Assinatura:

    aphabet_cesar_cipher = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 "
    
    # Esta classe é responsável por assinar digitalmente mensagens usando RSA, ou checar a assinatura de mensagens.
    @staticmethod
    def sign_message(private_key, message):
        '''Assina uma mensagem com a chave privada RSA. 
        O método de assinatura utiliza o padding PSS e o hash SHA256.'''
        signature = private_key.sign(
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return signature

    @staticmethod
    def decrypt_cesar (chave, cipherText):
        n = len(Assinatura.aphabet_cesar_cipher)
        plainText = ""

        for i in range(len(cipherText)):
            letra = cipherText[i]
            gt = Assinatura.search_alphabet(letra, Assinatura.aphabet_cesar_cipher)
            plainText += Assinatura.aphabet_cesar_cipher[(gt - chave) % n]

        print("texto descriptografado com a chave " + str(chave) + " : " + plainText)

    @staticmethod
    def encrypt_cesar (chave, plainText):
        n = len(Assinatura.aphabet_cesar_cipher)
        cipherText = ""

        for i in range(len(plainText)):
            letra = plainText[i]
            gt = Assinatura.search_alphabet(letra, Assinatura.aphabet_cesar_cipher)
            cipherText += Assinatura.aphabet_cesar_cipher[(gt + chave) % n]

        print("texto criptografado com a chave " + str(chave) + " : " + cipherText)
    
    @staticmethod 
    def search_alphabet(letra):
        for i in range(len(Assinatura.aphabet_cesar_cipher)):
            if Assinatura.aphabet_cesar_cipher[i] == letra:
                return i
