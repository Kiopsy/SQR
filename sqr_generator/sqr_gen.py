from typing import Sequence, Any
from qrcodegen import QrCode
from ecdsa import SigningKey, VerifyingKey
from certificate_authority import CertificateAuthority
import base64

class SQRCode(QrCode):
    def __init__(self, 
                 version: int, 
                 errcorlvl: QrCode.Ecc, 
                 datacodewords: bytes | Sequence[int], 
                 msk: int) -> None:
        
        super().__init__(version, errcorlvl, datacodewords, msk)

    @staticmethod
    def generate_signature(private_key_str: str, message: bytes) -> bytes:
        decoded_private_key_bytes = base64.b64decode(private_key_str)
        sk = SigningKey.from_string(decoded_private_key_bytes)
        return sk.sign(message)
    
    @staticmethod
    def generate_sqr_code(public_key_str: str, private_key_str: str, url: str, certificate_authority: CertificateAuthority) -> QrCode:

        # encrypt shortened_url with private key to get signed_url
        byte_url: bytes = url.encode('utf-8')
        signed_url: bytes = SQRCode.generate_signature(private_key_str, byte_url)

        # add new (url, signed_url) pair to Certificate Authority
        certificate_authority.register_url(public_key_str, url, signed_url)

        # encode pubkey and url into SQR code
        concatenator = "||"
        payload = url + concatenator + public_key_str

        return QrCode.encode_text(payload, QrCode.Ecc.MEDIUM)

    @staticmethod
    def print_sqr(qrcode: QrCode) -> None:
        """Prints the given QrCode object to the console."""
        border = 4
        for y in range(-border, qrcode.get_size() + border):
            for x in range(-border, qrcode.get_size() + border):
                print("\u2588 "[1 if qrcode.get_module(x,y) else 0] * 2, end="")
            print()
        print()
