class URLShortener:
    def __init__(self):
        # Mapping of top-level domains to their respective codes
        self.tld_mapping = {
            ".com": 0,
            ".org": 1,
            ".net": 2,
            ".co": 3,
            ".info": 4,
            ".io": 5,
            ".online": 6,
            ".xyz": 7,
            ".site": 8,
            ".biz": 9,
            ".app": 10,
            ".shop": 11,
            ".store": 12,
            ".tech": 13,
            ".fun": 14
        }

        # Reverse mapping of top-level domain codes to their respective domains
        self.reverse_tld_mapping = {v: k for k, v in self.tld_mapping.items()}

    def compress_url(self, url):
        parts = url.split('://')
        protocol = 1 if parts[0] == 'https' else 0
        domain, path = parts[1].split('/', 1)

        compressed_protocol = str(protocol)

        compressed_domain = self.compress_domain(domain)
        compressed_tld = self.compress_tld(domain)
        compressed_path = self.compress_path(path)

        compressed_url = compressed_protocol + compressed_domain + compressed_tld + compressed_path
        return compressed_url

    def compress_domain(self, domain):
        compressed_domain = ""
        for char in domain:
            if char.isalpha():
                # Encode letters from 1 to 26
                compressed_domain += str(ord(char.lower()) - ord('a') + 1)
            elif char == '.':
                compressed_domain += "27"
            elif char.isdigit():
                compressed_domain += str(int(char) + 27)
            elif char == '-':
                compressed_domain += "28"
            else:
                raise ValueError("Invalid character in domain")
        compressed_domain += "0"  # End of domain marker
        return compressed_domain

    def compress_tld(self, domain):
        tld = '.' + domain.split('.')[-1]
        if tld in self.tld_mapping:
            return format(self.tld_mapping[tld], '04b')
        else:
            return '1' + self.compress_domain(tld)

    def compress_path(self, path):
        # Base64 encoding would be used for path compression
        # For simplicity, we'll just return the length of the path
        return format(len(path), '06b')

    def decompress_url(self, compressed_url):
        protocol = "https" if compressed_url[0] == '1' else "http"
        domain = self.decompress_domain(compressed_url[1:11])
        tld = self.decompress_tld(compressed_url[11:15])
        path = self.decompress_path(compressed_url[15:])
        return f"{protocol}://{domain}.{tld}/{path}"

    def decompress_domain(self, compressed_domain):
        domain = ""
        i = 0
        while i < len(compressed_domain):
            code = int(compressed_domain[i:i+2])
            if code == 0:
                break
            elif code == 27:
                domain += "."
            elif code <= 26:
                domain += chr(ord('a') + code - 1)
            elif code <= 30:
                domain += str(code - 27)
            elif code == 31:
                i += 2
                domain += str(int(compressed_domain[i:i+3]) + 3)
                i += 2
            i += 2
        return domain

    def decompress_tld(self, compressed_tld):
        if compressed_tld[0] == '1':
            return self.decompress_domain(compressed_tld[1:])
        else:
            return self.reverse_tld_mapping[int(compressed_tld, 2)]

    def decompress_path(self, compressed_path):
        # For simplicity, we'll just return the length of the path
        return str(int(compressed_path, 2))


# Example usage:
url_shortener = URLShortener()
compressed_url = url_shortener.compress_url("https://docs.google.com/document")
print("Compressed URL:", compressed_url)

decompressed_url = url_shortener.decompress_url(compressed_url)
print("Decompressed URL:", decompressed_url)
