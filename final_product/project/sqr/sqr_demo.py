from ecdsa import SigningKey, VerifyingKey
from certificate_authority import CertificateAuthority
from sqr_code import SQRCode
from base64 import b64encode, b64decode

def simple():
     
    private_key: SigningKey = SigningKey.generate()
    private_key_str: str = b64encode(private_key.to_string()).decode('utf-8')

    public_key: VerifyingKey = private_key.verifying_key
    public_key_str = b64encode(public_key.to_string()).decode('utf-8')

    message = "Hello world"
    byte_message = message.encode('utf-8')

    sk = SigningKey.from_string(b64decode(private_key_str))
    signed_bytes = sk.sign(byte_message)
    signature = b64encode(signed_bytes).decode('utf-8')

    vk = VerifyingKey.from_string(b64decode(public_key_str))
    try:
        vk.verify(b64decode(signature.encode('utf-8')), byte_message)
        print("Worked")
        return True
    except:
        print("Failed")



def main():

    certificate_authority = CertificateAuthority()
	
    '''Register the user'''
    # Get users name and try to create public key
    username = input("Enter username: ")

    # User has their private key and public key
    private_key: SigningKey = SigningKey.generate()
    private_key_str: str = b64encode(private_key.to_string()).decode('utf-8')
    public_key: VerifyingKey = private_key.verifying_key


    # User gives us their public key
    public_key_str = b64encode(public_key.to_string()).decode('utf-8')

    # SERVER: We register the user
    if certificate_authority.register_user(public_key_str, username) == False:
        print("Cannot register user")
        return

    '''Shorten the url'''
    # User gives us a raw_url
    raw_url = input("Enter url: ")
    shortened_url = raw_url # TODO: SERVER: shorten based on our algo

    '''Sign the url'''
    # Done on the client -> user signs the url
    sk = SigningKey.from_string(b64decode(private_key_str))
    signed_bytes = sk.sign(shortened_url.encode('utf-8'))
    signature = b64encode(signed_bytes).decode('utf-8')

    
    # SERVER: add new (url, signed_url) pair to Certificate Authority
    certificate_authority.register_url(public_key_str, shortened_url, signature)
    
    '''Create SQR code'''
    # SERVER: generate an sqr code and give it to the user
    sqr_code = SQRCode.generate_sqr_code(public_key_str, shortened_url)
    SQRCode.print_sqr(sqr_code)
    SQRCode.save_sqr_as_image(sqr_code, 'sqr_test.png')

   
    


# Run the main program
if __name__ == "__main__":
	simple()
