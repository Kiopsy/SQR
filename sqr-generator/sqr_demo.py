from ecdsa import SigningKey
from certificate_authority import CertificateAuthority
from sqr_gen import SQRCode

def main():
	ca = CertificateAuthority()
	
    # Get users name and try to create public key
	user = input("What is your username?")
	
	private_key = SigningKey.generate()
	
	sqr_generator = SQRCode(ca, private_key)


# Run the main program
if __name__ == "__main__":
	main()