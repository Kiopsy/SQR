from flask import Blueprint, render_template, request, redirect, url_for, flash, make_response, jsonify, send_file
from flask_login import login_required, current_user
from . import db, certificate_authority


from .sqr.sqr_code import SQRCode
import io
from PIL import Image
import base64
from base64 import b64decode

main = Blueprint("main", __name__)

# @main.route('/')
# def index():
#     return render_template('index.html')

# Route to render HTML form
@main.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Process the POST request and generate the image
        # For example, generate_image_from_data(request.form['data'])

        # Sample code to generate a simple image using PIL
        img = Image.new('RGB', (200, 200), color='blue')
        # Convert the image to bytes
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes = img_bytes.getvalue()

        # Encode the image bytes to base64
        img_base64 = base64.b64encode(img_bytes).decode('utf-8')

        return render_template('index.html', image_data=img_base64)

    # Render the HTML form for GET request
    return render_template('index.html')


@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.name)

@main.route("/create_sqr_code", methods=["POST"])
@login_required
def profile_post():

    # data = request.get_json()

    public_key = current_user.public_key
    
    raw_url = request.form.get("url")
    if raw_url is None:
        print(1)
        return jsonify({"error": ""}), 400
    
    signature = request.form.get("signature")
    if signature is None:
        print(2)
        return jsonify({"error": ""}), 400
    
    # TODO: shorten the url
    shortened_url = raw_url
    
    # add new (url, signature) pair to Certificate Authority
    if certificate_authority.register_url(public_key, shortened_url, signature) == False:
        print(3)
        return jsonify({"error": ""}), 400

    sqr_code = SQRCode.generate_sqr_code(public_key, shortened_url)

    image_buffer = io.BytesIO()
    SQRCode.save_sqr_as_image(sqr_code, image_buffer)
    image_buffer.seek(0)

    image = Image.open(image_buffer)
    image.save("x.png")

    img_bytes = image_buffer.getvalue()
    img_base64 = base64.b64encode(img_bytes).decode('utf-8')
    
    print(4)
    return render_template('profile.html', image_data=img_base64)


@main.route('/scan')
def scan():
    return render_template('scan.html')

@main.route('/scan', methods=['POST'])
def scan_post():

    data = request.get_json()

    image_data = data.get('image_data')
    if image_data is None:
        return jsonify({"error": "No image provided"}), 400

    # Decode the base64-encoded image data
    image_data = image_data.split(',')[1]
    image_bytes = io.BytesIO(b64decode(image_data))

    # Create a PIL Image object from the decoded bytes
    pil_image = Image.open(image_bytes)


    image_data = SQRCode.decode_sqr_code(pil_image)
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