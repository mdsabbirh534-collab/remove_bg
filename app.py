import io
from flask import Flask, render_template, request, send_file
from PIL import Image
from rembg import remove

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'image' not in request.files:
        return "No file uploaded", 400
        
    file = request.files['image']
    if file.filename == '':
        return "No file selected", 400
        
    # ছবি ওপেন করা
    input_image = Image.open(file.stream)
    
    # ব্যাকগ্রাউন্ড রিমুভ করা (ফ্রি সার্ভারের জন্য অপ্টিমাইজড)
    output_image = remove(input_image)
    
    # মেমোরিতে সেভ করে ফেরত পাঠানো
    img_io = io.BytesIO()
    output_image.save(img_io, 'PNG')
    img_io.seek(0)
    
    return send_file(img_io, mimetype='image/png')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
