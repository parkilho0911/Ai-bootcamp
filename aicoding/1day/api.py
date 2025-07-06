from fastapi import FastAPI, File, UploadFile
import os
import uuid

import torch
from datasets import load_dataset
from transformers import EfficientNetImageProcessor, EfficientNetForImageClassification
from PIL import Image
import io
from ultralytics import YOLO


preprocessor = EfficientNetImageProcessor.from_pretrained("google/efficientnet-b0")
model = EfficientNetForImageClassification.from_pretrained("google/efficientnet-b0")

app = FastAPI()



# Directory to save uploaded images
UPLOAD_DIR = "uploaded_images"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/upload_image/")
async def upload_image(file: UploadFile = File(...)):
    """
    Uploads an image file to the server.
    """
    try:
        # Generate a unique filename to avoid collisions
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)

        # Read the file content and save it
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
        
        # Convert bytes to PIL Image
        image = Image.open(io.BytesIO(contents)).convert("RGB")

        inputs = preprocessor(image, return_tensors="pt")

        with torch.no_grad():
            logits = model(**inputs).logits

        # model predicts one of the 1000 ImageNet classes
        predicted_label = logits.argmax(-1).item()
        print(model.config.id2label[predicted_label]),

        return {
            "message": "Image uploaded successfully", 
            "filename": unique_filename, 
            "result": model.config.id2label[predicted_label]
        }
    except Exception as e:
        return {"message": f"Error uploading image: {e}"}

# To run this example:
# 1. Save the code as main.py
# 2. Run `uvicorn main:app --reload` in your terminal
# 3. Access the endpoint via a tool like Postman or a simple HTML form
#    sending a POST request to http://127.0.0.1:8000/upload_image/
#    with the image file in the request body as 'multipart/form-data'
#    with the field name 'file'.



@app.post("/upload_image2/")
async def upload_image2(file: UploadFile = File(...)):
    """
    Uploads an image file to the server.
    """
    try:
        # Generate a unique filename to avoid collisions
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)

        # Read the file content and save it
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
        
        # Convert bytes to PIL Image
        
        ymodel = YOLO("yolo11n.pt")
        result = ymodel.predict(source=file_path, save=True)

        return {
            "message": "Image uploaded successfully", 
            "filename": unique_filename, 
            "result": result
        }
    except Exception as e:
        return {"message": f"Error uploading image: {e}"}

