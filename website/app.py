from flask import Flask, render_template, request, redirect, jsonify
from PIL import Image
from pyzbar.pyzbar import decode
import io

app = Flask(__name__)

# load in the CA


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'photo' not in request.files:
        return jsonify({'error': 'No file part'})
    file = request.files['photo']
    if file.filename == '':
        return jsonify({'error': 'No selected file'})
    if file:
        image_stream = io.BytesIO(file.read())
        image = Image.open(image_stream)
        qr_codes = decode(image)
        if qr_codes:
            for obj in qr_codes:
                try: 
                    url, public_key_str = obj.data.decode('utf-8').split('||')
                    print('Url:', url)
                    print('Public Key:', public_key_str)
                except:
                    print("Invalid format. Not an SQR code.")
                    return None
        
    return jsonify({'error': 'No QR codes found'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
