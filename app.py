import io
import torch
from flask import Flask, render_template, request, send_file
from PIL import Image
from torchvision import transforms
from transformers import AutoModelForImageSegmentation

app = Flask(__name__)

# Load AI Model (BiRefNet)
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device} (Loading advanced BiRefNet model...)")

model = AutoModelForImageSegmentation.from_pretrained(
    "ZhengPeng7/BiRefNet", trust_remote_code=True
)
model.to(device)
model.eval()

image_size = (1024, 1024)
transform_image = transforms.Compose([
    transforms.Resize(image_size),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

def remove_background_advanced(input_image):
    orig_im_size = input_image.size
    input_images = transform_image(input_image).unsqueeze(0).to(device)
    
    with torch.no_grad():
        preds = model(input_images)[-1].sigmoid().cpu()
        
    pred = preds[0].squeeze()
    pred_pil = transforms.ToPILImage()(pred).resize(orig_im_size)
    
    output_image = input_image.copy()
    output_image.putalpha(pred_pil)
    return output_image

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
        
    input_image = Image.open(file.stream).convert("RGB")
    output_image = remove_background_advanced(input_image)
    
    img_io = io.BytesIO()
    output_image.save(img_io, 'PNG')
    img_io.seek(0)
    return send_file(img_io, mimetype='image/png')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
