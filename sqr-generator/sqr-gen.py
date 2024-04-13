from typing import Sequence
from qrcodegen import QrCode

class SQRCode(QrCode):
    def __init__(self, version: int, errcorlvl: QrCode.Ecc, datacodewords: bytes | Sequence[int], msk: int) -> None:
        super().__init__(version, errcorlvl, datacodewords, msk)
        
    def get_certificate_from_url() -> str:
        pass 