from typing import Any, Tuple, Union, Dict, List
from ecdsa import SigningKey, VerifyingKey, NIST192p, BadSignatureError
import base64
import pickle
import os

class CertificateAuthority():
    def __init__(self) -> None:
        # public key str -> [name of signer (e.g. "Harvard"), dict{website (e.g. "my.harvard.edu") -> its signed_url}]
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
    def register_user(self, public_key_str: str, user: str) -> bool:
        if public_key_str in self.log:
            print("Error: this public key already exists in the logs")
            return False
        
        if user in self.users:
            print("Error: this user already exists in the logs")
            return False
            
        self.log[public_key_str] = (user, {})
        self.users.add(user)
        self.save_log()
        return True
    
    def verify_signed_url(self, public_key_str: str, url: str, signed_url: bytes) -> bool:
        # vk = VerifyingKey.from_string(public_key, curve=NIST192p)
        decoded_public_key_bytes = base64.b64decode(public_key_str)
        vk = VerifyingKey.from_string(decoded_public_key_bytes)

        try:
            vk.verify(bytes(url, "ascii"), signed_url)
            print(f"Site registered: {url}")
            return True
        except BadSignatureError:
            print(f"Bad signed_url detected by certificate authority for url {url}")
        
        return False

    # Take a signed message from an SQR code creator containing a url 
    # we want to insert. If the signed_url isn't valid, ignore the message.
    def register_url(self, public_key_str: str, url: str, signed_url: bytes) -> None:
        if self.verify_signed_url(public_key_str, url, signed_url) == False:
            return None

        value = self.log.get(public_key_str)
        if not value:
            return None
        _, url_to_signed_url = value
        
        if url in url_to_signed_url:
            print("signed_url already exists for this url")
            return None
    
        url_to_signed_url[url] = signed_url
        self.save_log()
    
    # Take a signed url contained in an SQR code and return its signed_url and the
    # identity of the signer.
    # If the URL wasn't previously signed by this public key, returns None.
    def get_signed_url(self, public_key_str: str, url: str) -> Tuple[str, bytes] | None:
        value = self.log.get(public_key_str)
        if value is None:
            return None

        identity, url_to_signed_url = value

        signed_url = url_to_signed_url.get(url)
        if signed_url is None:
            return None
        
        return identity, signed_url
