from datetime import datetime
import json
from ..service import WriterService
from ..security.diffie_helman import Diffie_Helman
from ..security.translate_pem import Translate_Pem
import base64

# session key usa writerService para fazer autosave
class SessionKey:
    def __init__(self, target, parametros = None, salt = None, chave_publica = None):
        self.target = target
        self.parametros = parametros
        self.salt = salt
        self.dh_chave_publica = chave_publica

    def primeiro_aes_e_hmac(self):
        from ..security import Diffie_Helman
        from ..service import WriterService

        # quando voce é o primeiro, vc usa os parametros para gerar uma dh_private_key e uma dh_public
        dh_private, dh_public = Diffie_Helman.generate_temporary_keys(self.parametros)

        # Gera a chave de sessão usando a chave privada temporária e a chave pública do destinatário.
        self.aes_key, self.hmac_key = Diffie_Helman.exchange_and_derive_key(dh_private, self.dh_chave_publica, self.salt)
        self.save_session_key()

        return dh_public

    def segunda_aes_e_hmac(self, chave_publica_resposta, dh_private_key, salt):
        from ..security import Diffie_Helman
        # gera a segunda chave de sessao pelo Diffie Helman 3
        self.aes , self.hmac = Diffie_Helman.exchange_and_derive_key(dh_private_key, chave_publica_resposta, salt)
        self.save_session_key()

    def to_json(self):
        return json.dumps({
            "target" : self.target,
            "aes_key": base64.b64encode(self.aes_key).decode('utf-8'),  # Chave AES em formato string
            "hmac_key": base64.b64encode(self.hmac_key).decode('utf-8'),  # Chave HMAC em formato string
            "creation_time": datetime.now().strftime("%H:%M"),
            "valid" : True
        }, indent=2)

    def is_expired(self):
        return datetime.now().strftime("%H:%M") > self.creation_time + self.expiration_seconds

    def check_session_key(self):
        if self.is_expired():
            self.valid = False
            self.save_session()
        return self.valid

    def count_limit(self):
        if self.remaining_messages <= 0:
            self.valid = False
        else:
            self.remaining_messages -= 1
        self.save_session()
        return self.valid

    def save_session_key(self):
        from ..service import WriterService
        WriterService.insert_session_key(self.to_json(), self.target)
        print("session key feita")
