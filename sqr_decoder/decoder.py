from pyzbar.pyzbar import decode
from PIL import Image

def decode_qr_code(image_path):
    img = Image.open(image_path)
    decoded_objects = decode(img)
    
    if decoded_objects:
        for obj in decoded_objects:
            print("Type:", obj.type)
            print("Data:", obj.data.decode('utf-8'))
    else:
        print("No QR code found.")

# Specify the path to your QR code image that was just generated
decode_qr_code("test.png")