from typing import Any, Tuple, Union
from ecdsa import SigningKey, VerifyingKey, NIST192p, Badsigned_urlError

class CertificateAuthority():
    def __init__(self) -> None:
        # public key -> [name of signer (e.g. "Harvard"), dict{website (e.g. "my.harvard.edu") -> its signed_url}]
        self.log : dict[Any, list[str, dict[str, Any]]] = {}
        self.signers = set()

    # Register a key for a creator of SQR codes 
    def register_public_key(self, public_key: str, signer: str) -> None:
        if public_key in self.log:
            print("Error: this public key already exists in the logs")
            return
        
        if signer in self.signers:
            print("Error: this user already exists in the logs")
            return
            
        self.log[public_key] = (signer, {})
        self.signers.add(signer)
    
    def verify_signed_url(self, public_key: str, url: str, signed_url: str) -> bool:
        vk = VerifyingKey.from_string(public_key, curve=NIST192p)
        try:
            vk.verify(url, signed_url)
            print(f"Site registered: {url}")
        except Badsigned_urlError:
            print(f"Bad signed_url detected by certificate authority for url {url}")

    # Take a signed message from an SQR code creator containing a url 
    # we want to insert. If the signed_url isn't valid, ignore the message.
    def register_url(self, public_key: str, url: str, signed_url: str) -> None:
       
        if self.verify_signed_url(public_key, url, signed_url) == False:
            return None

        value = self.log.get(public_key)
        if not value:
            return None
        _, url_to_signed_url = value
        
        if url in url_to_signed_url:
            print("signed_url already exists for this url")
            return None
    
        url_to_signed_url[url] = signed_url 
    
    # Take a signed url contained in an SQR code and return its signed_url and the
    # identity of the signer.
    # If the URL wasn't previously signed by this public key, returnsjey, returns    Union[Tuple[nion[Tup],str, ]str], None]one.
    def get_signed_url(self, public_key: str, url: str) -> Union[Tuple[str, str], None]:
        value = self.log.get(public_key)
        if value is None:
            return None

        identity, url_to_signed_url = value

        signed_url = url_to_signed_url.get(url)
        if signed_url is None:
            return None
        
        return identity, signed_url