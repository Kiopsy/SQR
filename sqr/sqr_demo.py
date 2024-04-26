from ecdsa import SigningKey, VerifyingKey
from certificate_authority import CertificateAuthority
from sqr.sqr_code import SQRCode
import base64

def main():
    
    # private_key = SigningKey.generate()
    # public_key = private_key.verifying_key

    # # Sign a message using the original private key
    # msg = "Hello, world!"
    # message = msg.encode('utf-8')
    # signature = private_key.sign(message)

    # # Verify the signature using the corresponding public key
    # is_valid = public_key.verify(signature, message)

    # print("Signature verification:", is_valid)
    # return

    certificate_authority = CertificateAuthority()
	
    # Get users name and try to create public key
    username = input("Enter username: ")
    private_key: SigningKey = SigningKey.generate()
    public_key: VerifyingKey = private_key.verifying_key

    private_key_str = base64.b64encode(private_key.to_string()).decode('utf-8')
    public_key_str = base64.b64encode(public_key.to_string()).decode('utf-8')


    if certificate_authority.register_user(public_key_str, username) == False:
        print("Cannot register user")
        return

    raw_url = input("Enter url: ")
	
    sqr_code = SQRCode.generate_sqr_code(public_key_str, private_key_str, raw_url, certificate_authority)

    SQRCode.print_sqr(sqr_code)
    SQRCode.save_sqr_as_image(sqr_code, 'sqr_test.png')


# Run the main program
if __name__ == "__main__":
	main()
