from typing import Sequence, Any
from .qrcodegen import QrCode
# from pyzbar.pyzbar import decode
from PIL import Image

class SQRCode(QrCode):

    concatenator = "||"

    def __init__(self, 
                 version: int, 
                 errcorlvl: QrCode.Ecc, 
                 datacodewords: bytes | Sequence[int], 
                 msk: int) -> None:
        
        super().__init__(version, errcorlvl, datacodewords, msk)

    
    @staticmethod
    def generate_sqr_code(public_key_str: str, url: str) -> QrCode:
        """Encode pubkey and url into SQR code"""

        payload = url + SQRCode.concatenator + public_key_str
        return QrCode.encode_text(payload, QrCode.Ecc.MEDIUM)
    
    @staticmethod
    def decode_sqr_code(image: Image) -> tuple[str, str] | None:
        # open the image and use pyzbar to decode
        decoded_objects = decode(image)
        # go through all possible decoded objects
        if decoded_objects:
            for obj in decoded_objects:
                # a decoded SQR should be: 'url || public_key_str'
                try: 
                    url, public_key_str = obj.data.decode('utf-8').split(SQRCode.concatenator)
                    return url, public_key_str
                except:
                    print("Invalid format. Not an SQR code.")
                    return None
        else:
            print("No QR code found.")
            return None

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
    def save_sqr_as_image(qrcode: QrCode, buffer: Any) -> None:
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

        image.save(buffer, format="png")
