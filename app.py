from flask import Flask, render_template, request, redirect, url_for, send_file
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
import os
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO

load_dotenv(dotenv_path=os.path.join(os.getcwd(), '.env'))

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("GEMINI_API_KEY is not set in the .env file")

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}
client = genai.Client(api_key=API_KEY)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/', methods=['GET', 'POST'])
def index():
    image_url = None
    if request.method == 'POST':
        if 'image' not in request.files or 'prompt' not in request.form:
            return 'No file part or prompt'
        file = request.files['image']
        prompt = request.form['prompt']
        if file.filename == '':
            return 'No selected file'
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            image = Image.open(filepath)
            response = client.models.generate_content(
                model='gemini-2.0-flash-exp-image-generation',
                contents=[prompt, image],
                config=types.GenerateContentConfig(
                    response_modalities=['Text', 'Image']
                )
            )

            for part in response.candidates[0].content.parts:
                if part.inline_data is not None:
                    new_image = Image.open(BytesIO(part.inline_data.data))
                    processed_filename = 'watermark_removed.png'
                    new_image.save(os.path.join(app.config['UPLOAD_FOLDER'], processed_filename))
                    image_url = url_for('uploaded_file', filename=processed_filename)
                    break
            if image_url is None:
                return 'Failed to process image'
    return render_template('index.html', image_url=image_url)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename))

if __name__ == '__main__':
    app.run(debug=True)