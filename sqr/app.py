from flask import Flask, jsonify, request, make_response
import json
import io

from ecdsa import SigningKey, VerifyingKey
from certificate_authority import CertificateAuthority
from sqr.sqr_code import SQRCode
from PIL import Image

app = Flask(__name__)

certificate_authority = CertificateAuthority()

@app.route("/")
def home():
    return "Welcome to SQR!"

@app.route("/register_user", methods=["POST"])
def register_user():
    user_info = json.loads(request.data)

    username : str = user_info.get("username")
    if username is None:
        return jsonify({"error": "No username specified"}), 400
    
    public_key : str = user_info.get("public_key")
    if public_key is None:
        return jsonify({"error": "No public_key specified"}), 400


    if certificate_authority.register_user(public_key, username) == False:
        return jsonify({"error": "Cannot register this username"}), 400
    
    return '', 201

@app.route("/register_user", methods=["POST"])
def register_user():

    req = json.loads(request.data)

    username : str = req.get("username")
    if username is None:
        return jsonify({"error": "No username specified"}), 400
    
    public_key : str = req.get("public_key")
    if public_key is None:
        return jsonify({"error": "No public_key specified"}), 400


    if certificate_authority.register_user(public_key, username) == False:
        return jsonify({"error": "Cannot register this username"}), 400
    
    return {}, 201

@app.route("/create_sqr_code", methods=["POST"])
def create_sqr_code():

    req = json.loads(request.data)

    public_key : str = req.get("public_key")
    if public_key is None:
        return jsonify({"error": "No public_key specified"}), 400
    
    shortened_url : str = req.get("shortened_url")
    if shortened_url is None:
        return jsonify({"error": "No shortened_url specified"}), 400
    
    signed_url : bytes = req.get("signed_url")
    if signed_url is None:
        return jsonify({"error": "No signed_url specified"}), 400
    
    # add new (url, signed_url) pair to Certificate Authority
    if certificate_authority.register_url(public_key, shortened_url, signed_url) == False:
        return jsonify({"error": "Cannot register this url"}), 400

    sqr_code = SQRCode.generate_sqr_code(public_key, shortened_url)
    SQRCode.print_sqr(sqr_code)

    img_io = io.BytesIO()
    SQRCode.save_sqr_as_image(sqr_code, img_io)
    img_io.seek(0)
    
    # Create a response with the image data
    response = make_response(img_io.getvalue())
    response.headers['Content-Type'] = 'image/png'

    """
    <!-- Using JavaScript AJAX -->
    <script>
        fetch('/get_image')
            .then(response => response.blob())
            .then(blob => {
                var objectURL = URL.createObjectURL(blob);
                document.getElementById('myImage').src = objectURL;
            });
    </script>
    """
    
    return response

@app.route('/scan_qr', methods=['POST'])
def scan_qr():

    image_file = request.files.get("image")
    if image_file is None or image_file.filename == '':
        return jsonify({"error": "No image provided"}), 400


    image_stream = io.BytesIO(image_file.read())
    image = Image.open(image_stream)
    
    image_data = SQRCode.decode_sqr_code(image)
    if image_data is None:
        return jsonify({"error": "No SQR code detected"}), 400
    url, public_key = image_data

    signature_info = certificate_authority.get_signature(public_key, url)
    if signature_info is None:
        return jsonify({"error": "No signature found"}), 400
    _, signed_url = signature_info

    if certificate_authority.verify_signature(public_key, url, signed_url) == False:
        return jsonify({"error": "Cannot verify signature"}), 400

    return jsonify({"data": url}), 200
    
if __name__ == "__main__":
    host, port = "0.0.0.0", 5000
    app.run(host= host, port= port, debug=True)
    print(f"Server now running at {host}:{port}")