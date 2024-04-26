from typing import Any, Tuple, Union
from ecdsa import SigningKey, VerifyingKey, NIST192p, BadSignatureError
import base64

class CertificateAuthority():
    def __init__(self) -> None:
        # public key str -> [name of signer (e.g. "Harvard"), dict{website (e.g. "my.harvard.edu") -> its signed_url}]
        self.log : dict[str, list[str, dict[str, Any]]] = {}
        self.users = set()

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
        return True
    
    def verify_signed_url(self, public_key_str: str, byte_url: bytes, signed_url: bytes) -> bool:
        # vk = VerifyingKey.from_string(public_key, curve=NIST192p)
        decoded_public_key_bytes = base64.b64decode(public_key_str)
        vk = VerifyingKey.from_string(decoded_public_key_bytes)

        try:
            vk.verify(byte_url, signed_url)
            print(f"Site registered: {byte_url.decode()}")
            return True
        except BadSignatureError:
            print(f"Bad signed_url detected by certificate authority for url {byte_url.decode()}")
        
        return False

    # Take a signed message from an SQR code creator containing a url 
    # we want to insert. If the signed_url isn't valid, ignore the message.
    def register_url(self, public_key_str: str, byte_url: bytes, signed_url: bytes) -> None:
       
        if self.verify_signed_url(public_key_str, byte_url, signed_url) == False:
            return None

        value = self.log.get(public_key_str)
        if not value:
            return None
        _, url_to_signed_url = value
        
        if byte_url in url_to_signed_url:
            print("signed_url already exists for this url")
            return None
    
        url_to_signed_url[byte_url] = signed_url 
    
    # Take a signed url contained in an SQR code and return its signed_url and the
    # identity of the signer.
    # If the URL wasn't previously signed by this public key, returnsjey, returns    Union[Tuple[nion[Tup],str, ]str], None]one.
    def get_signed_url(self, public_key_str: str, byte_url: bytes) -> tuple[str, bytes] | None:
        value = self.log.get(public_key_str)
        if value is None:
            return None

        identity, url_to_signed_url = value

        signed_url = url_to_signed_url.get(byte_url)
        if signed_url is None:
            return None
        
        return identity, signed_url