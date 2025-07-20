import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from model import train_model
from db import init_db, add_user, check_user
import pytesseract
import cv2
from PIL import Image

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

model = train_model()
init_db()

def extract_text(image_path):
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
    text = pytesseract.image_to_string(thresh)
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    return lines

@app.route("/upload", methods=["POST"])
def upload_file():
    print("Upload route called")
    print("Files received:", request.files)
    if "file" not in request.files:
        print("No file uploaded")
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    print(f"Received file: {file.filename}")
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    lines = extract_text(filepath)
    results = [{"field": model.predict([line])[0], "value": line} for line in lines]
    print("Extraction results:", results)

    return jsonify({"results": results})

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    print("Register data received:", data)
    if add_user(data['username'], data['password']):
        print(f"User {data['username']} registered successfully")
        return jsonify({"message": "User registered successfully"}), 201
    print(f"User {data['username']} registration failed: already exists")
    return jsonify({"error": "Username already exists"}), 409

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    print("Login data received:", data)
    if check_user(data['username'], data['password']):
        print("Login successful")
        return jsonify({"message": "Login successful!"}), 200
    print("Login failed")
    return jsonify({"error": "Invalid credentials"}), 401

if __name__ == "__main__":
    app.run(port=5000, debug=True)
