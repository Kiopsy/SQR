from typing import Any, Tuple, Dict
from ecdsa import VerifyingKey, BadSignatureError
from base64 import b64decode
import pickle
import os

class CertificateAuthority():
    def __init__(self) -> None:
        # public key str -> [username of signer (e.g. "Harvard"), dict{website (e.g. "my.harvard.edu") -> its signed_url}]
        if not os.path.exists("log.pickle"):
            self.log : Dict[str, Tuple[str, Dict[str, Any]]] = {}
            self.save_log()
        else:
            with open('log.pickle', 'rb') as handle:
                self.log = pickle.load(handle)
        self.users = set()

    def save_log(self) -> None:
        with open('log.pickle', 'wb') as handle:
            pickle.dump(self.log, handle, protocol=pickle.HIGHEST_PROTOCOL)

    # Register a key for a creator of SQR codes 
    def register_user(self, public_key: str, user: str) -> bool:
        if public_key in self.log:
            print("Error: this public key already exists in the logs")
            return False
        
        if user in self.users:
            print("Error: this user already exists in the logs")
            return False
            
        self.log[public_key] = (user, {})
        self.users.add(user)
        self.save_log()
        return True
    
    def verify_signature(self, public_key: str, message: str, signature: str) -> bool:

        try:
            vk = VerifyingKey.from_string(b64decode(public_key))
            byte_message = message.encode('utf-8')
            byte_signature = b64decode(signature.encode('utf-8'))
            vk.verify(byte_signature, byte_message)
            return True
        except:
            print(f"Could not verify signature for {message}")
        
        return False

    # Take a signed message from an SQR code creator containing a url 
    # we want to insert. If the signed_url isn't valid, ignore the message.
    def register_url(self, public_key: str, url: str, signature: str) -> bool:
        if self.verify_signature(public_key, url, signature) == False:
            return False

        value = self.log.get(public_key)
        if value is None:
            return False
        _, url_to_signature = value
    
        url_to_signature[url] = signature
        self.save_log()
        return True
    
    # Take a signed url contained in an SQR code and return its signed_url and the
    # identity of the signer.
    # If the URL wasn't previously signed by this public key, returns None.
    def get_signature(self, public_key: str, url: str) -> Tuple[str, bytes] | None:
        
        value = self.log.get(public_key)
        if value is None:
            return None
        identity, url_to_signature = value

        signature = url_to_signature.get(url)
        if signature is None:
            return None
        
        return identity, signature