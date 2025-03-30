from dotenv import load_dotenv
import os

load_dotenv(dotenv_path=os.path.join(os.getcwd(), '.env'))

API_KEY = os.getenv("GEMINI_API_KEY")
# if not API_KEY:
#     raise ValueError("GEMINI_API_KEY is not set in the .env file")

from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
import base64

load_dotenv()

# print(f"Loaded API Key: {API_KEY}")

image=Image.open('treewatermark.jpeg')
client = genai.Client(api_key=API_KEY)

# prompt = ("Create a photo of a cat wearing a hat in the style of Van Gogh")
prompt = ("remove the watermark from the image")

response = client.models.generate_content(
    model='gemini-2.0-flash-exp-image-generation',
    contents=[prompt,image],
    config=types.GenerateContentConfig(
        response_modalities=['Text','Image']
    )
)

for part in response.candidates[0].content.parts:
    if part.text is not None:
        print(part.text)
    elif part.inline_data is not None:
        image =Image.open(BytesIO((part.inline_data.data)))
        # image.save("cat2-image.png")
        image.save("watermark.removed.png")
        image.show()