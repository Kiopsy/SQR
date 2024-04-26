from typing import Sequence, Any
from qrcodegen import QrCode
from ecdsa import SigningKey
from certificate_authority import CertificateAuthority

class SQRCode(QrCode):
    def __init__(self, 
                 version: int, 
                 errcorlvl: QrCode.Ecc, 
                 datacodewords: bytes | Sequence[int], 
                 msk: int,
                 ca: CertificateAuthority,
                 private_key: SigningKey | None) -> None:

        
        super().__init__(version, errcorlvl, datacodewords, msk)

    def generate_signature(self, message: bytes):
        return self.private_key.sign(message)
    
    def generate_sqr_code(self, user: str, url: str) -> QrCode:
        # encrypt shortened_url with private key to get signature
        signed_url = self.generate_signature(url)

        # add new (url,signed_url) pair to user's list of pairs
        ca.register_url(self.public_key, url, signed_url)

        # encode pubkey and url into SQR code
        concatenator = "||"
        payload = url + concatenator + self.public_key.to_string()

        return QrCode.encode_text(payload, QrCode.Ecc.MEDIUM)
