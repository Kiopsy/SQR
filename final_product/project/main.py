from flask import Blueprint, render_template, request, jsonify, flash
from flask_login import login_required, current_user
from . import db, certificate_authority
from .sqr.sqr_code import SQRCode
import io
from PIL import Image
import base64

# Define a Blueprint for the main routes
main = Blueprint("main", __name__)

# Route for the index page
@main.route('/')
def index():
    return render_template('index.html')


@main.route('/create')
@login_required
def create():
    return render_template('create.html', name=current_user.name)

@main.route("/create", methods=["POST"])
@login_required
def create_post():

    public_key = current_user.public_key

    data = request.get_json()

    raw_url = data.get("url")
    if raw_url is None:
        error_msg = "No url given"
        flash(error_msg)
        return jsonify({"error": error_msg}), 400
    
    signature = data.get("signature")
    if signature is None:
        error_msg = "No signature given"
        flash(error_msg)
        return jsonify({"error": error_msg}), 400
    
    # TODO: Shorten the URL (TO-DO: Implement URL shortening logic)
    shortened_url = raw_url
    
    # Register the URL with the Certificate Authority
    if not certificate_authority.register_url(public_key, shortened_url, signature):
        error_msg = "Failed to register url with Certificate Authority"
        flash(error_msg)
        return jsonify({"error": error_msg}), 400
    
    # Generate and save the SQR code image
    sqr_code = SQRCode.generate_sqr_code(public_key, shortened_url)
    image_buffer = io.BytesIO()
    SQRCode.save_sqr_as_image(sqr_code, image_buffer)
    image_buffer.seek(0)
    
    # Convert the image to base64 format
    img_bytes = image_buffer.getvalue()
    img_base64 = base64.b64encode(img_bytes).decode('utf-8')
    
    return jsonify({"image_data": img_base64})

# Route for displaying the scan page
@main.route('/scan')
def scan():
    return render_template('scan.html')

# Route for processing the scanned SQR code
@main.route('/scan', methods=['POST'])
def scan_post():
    data = request.get_json()
    image_data = data.get('image_data')
    if image_data is None:
        return jsonify({"error": "No image provided"}), 400
    
    # Decode the base64-encoded image data
    image_data = image_data.split(',')[1]
    image_bytes = io.BytesIO(base64.b64decode(image_data))
    
    # Create a PIL Image object from the decoded bytes
    pil_image = Image.open(image_bytes)
    
    # Decode the SQR code from the image
    image_data = SQRCode.decode_sqr_code(pil_image)
    if image_data is None:
        return jsonify({"error": "No SQR code detected"}), 400
    url, public_key = image_data
    
    # Retrieve signature information from the Certificate Authority
    signature_info = certificate_authority.get_signature(public_key, url)
    if signature_info is None:
        return jsonify({"error": "No signature found"}), 400
    _, signed_url = signature_info
    
    # Verify the signature
    if not certificate_authority.verify_signature(public_key, url, signed_url):
        return jsonify({"error": "Cannot verify signature"}), 400
    
    return jsonify({"data": url}), 200
