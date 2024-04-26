from typing import Sequence, Any
from qrcodegen import QrCode
from ecdsa import SigningKey, VerifyingKey
from certificate_authority import CertificateAuthority
import base64
from pyzbar.pyzbar import decode
from PIL import Image

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
    def decode_sqr_code(image_path: str, certificate_authority: CertificateAuthority) -> str | None:
        # open the image and use pyzbar to decode
        img = Image.open(image_path)
        decoded_objects = decode(img)
        
        # go through all possible decoded objects
        if decoded_objects:
            for obj in decoded_objects:
                # a decoded SQR should be: 'url || public_key_str'
                try: 
                    url, public_key_str = obj.data.decode('utf-8').split('||')
                except:
                    print("Invalid format. Not an SQR code.")
                    return None

                # check the url signature with the CA
                signed_url = certificate_authority.get_signed_url(public_key_str, url)
                if certificate_authority.verify_signed_url(public_key_str, url, signed_url):
                    return url
                else:
                    print("Invalid SQR is not secure.")
                    return None
        else:
            print("No QR code found.")

    @staticmethod
    def print_sqr(qrcode: QrCode) -> None:
        """Prints the given QrCode object to the console."""
        border = 4
        for y in range(-border, qrcode.get_size() + border):
            for x in range(-border, qrcode.get_size() + border):
                print("\u2588 "[1 if qrcode.get_module(x,y) else 0] * 2, end="")
            print()
        print()

    @staticmethod
    def save_sqr_as_image(qrcode: QrCode, file_path: str) -> None:
        """Saves the given QrCode object as an image file."""
        border = 1
        scale = 10  # This scale factor will determine the size of each module in the QR code
        size = qrcode.get_size() + 2 * border

        # create a blank white image
        image = Image.new("1", (size * scale, size * scale), "white")

        # put the QR code in the image
        start_x = start_y = border * scale
        for y in range(qrcode.get_size()):
            for x in range(qrcode.get_size()):
                color = 0 if qrcode.get_module(x, y) else 1  # 0 is black, 1 is white
                for dy in range(scale):
                    for dx in range(scale):
                        # Set the pixel values adjusting for the border offset
                        image.putpixel((start_x + x * scale + dx, start_y + y * scale + dy), color)

        image.save(file_path, "PNG")
