from flask import Blueprint, render_template, request, jsonify, flash, redirect
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
    return render_template('create.html', name=current_user.name, url="", signature="", image_data="")

@main.route("/create", methods=["POST"])
@login_required
def create_post():

    public_key = current_user.public_key

    data = request.form #request.get_json()

    raw_url = data.get("url")
    if raw_url is None:
        error_msg = "No url given"
        flash(error_msg)
        return render_template('create.html', name=current_user.name, url="", signature="", image_data="")
        # return jsonify({"error": error_msg}), 400
    
    signature = data.get("signature")
    if signature is None:
        error_msg = "No signature given"
        flash(error_msg)
        return render_template('create.html', name=current_user.name, url=raw_url, signature="", image_data="")
        # return jsonify({"error": error_msg}), 400
    
    # TODO: Shorten the URL (TO-DO: Implement URL shortening logic)
    shortened_url = raw_url
    
    # Register the URL with the Certificate Authority
    if not certificate_authority.register_url(public_key, shortened_url, signature):
        error_msg = "Failed to register url with Certificate Authority"
        flash(error_msg)
        return render_template('create.html', name=current_user.name, url=raw_url, signature=signature, image_data="")
        # return jsonify({"error": error_msg}), 400
    
    # Generate and save the SQR code image
    sqr_code = SQRCode.generate_sqr_code(public_key, shortened_url)
    image_buffer = io.BytesIO()
    SQRCode.save_sqr_as_image(sqr_code, image_buffer)
    Image.open(image_buffer).save("x.png")
    image_buffer.seek(0)
    
    # Convert the image to base64 format
    img_bytes = image_buffer.getvalue()
    img_base64 = base64.b64encode(img_bytes).decode('utf-8')
    
    return render_template('create.html', name=current_user.name, url=raw_url, signature=signature, image_data=f"data:image/png;base64,{img_base64}")
    # return jsonify({"image_data": img_base64})

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
        print(1)
        return jsonify({"success": False, "message": "No image provided"}), 400
    
    try:
        # Decode the base64-encoded image data
        image_data = image_data.split(',')[1]
        image_bytes = io.BytesIO(base64.b64decode(image_data))
        
        # Create a PIL Image object from the decoded bytes
        pil_image = Image.open(image_bytes)
        
        # Decode the SQR code from the image
        image_data = SQRCode.decode_sqr_code(pil_image)
        if image_data is None:
            print(2)
            return jsonify({"success": False, "message": "No SQR code detected"})
        
        message, public_key = image_data
        
        # Retrieve signature information from the Certificate Authority
        signature_info = certificate_authority.get_signature(public_key, message)
        if signature_info is None:
            print(3)
            return jsonify({"success": False, "message": "No signature found"})
        identity, signed_message = signature_info
        
        # Verify the signature
        if certificate_authority.verify_signature(public_key, message, signed_message) == False:
            print(4)
            return jsonify({"success": False, "message": "Cannot verify signature"})
        
        print(5)
        return jsonify({"success": True, "message": message, "identity": identity}), 200
    except Exception as e:
        print(6, e)
        return jsonify({"success": False, "message": str(e)}), 400


