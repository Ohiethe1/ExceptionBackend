import os
from flask import Flask, request, jsonify, g
from flask_cors import CORS
from model import train_model
from db import init_db, add_user, check_user
import pytesseract
import cv2
from PIL import Image
import re
from db import init_exception_form_db, store_exception_form
from exception_codes import exception_codes
import sqlite3

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

@app.route('/api/stats', methods=['GET'])
def get_stats():
    conn = sqlite3.connect('forms.db')
    c = conn.cursor()
    # Sum overtime (convert HH:MM to minutes, then back to HH:MM)
    c.execute('SELECT overtime_hh, overtime_mm FROM exception_form_rows')
    total_minutes = 0
    for hh, mm in c.fetchall():
        try:
            total_minutes += int(hh or 0) * 60 + int(mm or 0)
        except Exception:
            continue
    total_overtime_hh = total_minutes // 60
    total_overtime_mm = total_minutes % 60
    # Count unique TA job numbers (non-empty)
    c.execute('SELECT COUNT(DISTINCT ta_job_no) FROM exception_form_rows WHERE ta_job_no != ""')
    total_job_numbers = c.fetchone()[0]
    conn.close()
    return jsonify({
        'total_overtime': f"{total_overtime_hh:02d}:{total_overtime_mm:02d}",
        'total_job_numbers': total_job_numbers
    })

def parse_exception_form(ocr_lines):
    # This is a simplified parser. You may need to adjust regexes for your OCR output.
    form_data = {
        'pass_number': '',
        'title': '',
        'employee_name': '',
        'rdos': '',
        'actual_ot_date': '',
        'div': '',
        'comments': '',
        'supervisor_name': '',
        'supervisor_pass_no': '',
        'oto': '',
        'oto_amount_saved': '',
        'entered_in_uts': ''
    }
    rows = []

    # Example: parse header fields
    for line in ocr_lines:
        if "Pass Number" in line:
            form_data['pass_number'] = line.split()[-1]
        elif "Title" in line:
            form_data['title'] = line.split()[-1]
        elif "Employee Name" in line:
            form_data['employee_name'] = line.split(":")[-1].strip()
        # ...repeat for other fields

    # Example: parse table rows (very basic, you may need to improve this)
    table_start = False
    for line in ocr_lines:
        if re.match(r'\d{2,4}', line.strip().split()[0]):  # If line starts with a code
            table_start = True
        if table_start:
            parts = line.split()
            if len(parts) >= 10:  # crude check for a table row
                code = parts[0]
                code_description = exception_codes.get(code, "")
                row = {
                    'code': code,
                    'code_description': code_description,
                    'line_location': parts[1],
                    'run_no': parts[2],
                    'exception_time_from_hh': parts[3],
                    'exception_time_from_mm': parts[4],
                    'exception_time_to_hh': parts[5],
                    'exception_time_to_mm': parts[6],
                    'overtime_hh': parts[7],
                    'overtime_mm': parts[8],
                    'bonus_hh': parts[9],
                    'bonus_mm': parts[10],
                    'nite_diff_hh': parts[11] if len(parts) > 11 else '',
                    'nite_diff_mm': parts[12] if len(parts) > 12 else '',
                    'ta_job_no': parts[13] if len(parts) > 13 else ''
                }
                rows.append(row)
    return form_data, rows

# Example usage after OCR:
ocr_lines = [
    # ...lines from your OCR output...
]
init_exception_form_db()
form_data, rows = parse_exception_form(ocr_lines)
store_exception_form(form_data, rows)

def init_audit_db():
    conn = sqlite3.connect('forms.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS audit_trail (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            action TEXT,
            target_type TEXT,
            target_id INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            details TEXT
        )
    ''')
    conn.commit()
    conn.close()

def log_audit(username, action, target_type, target_id, details=""):
    conn = sqlite3.connect('forms.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO audit_trail (username, action, target_type, target_id, details)
        VALUES (?, ?, ?, ?, ?)
    ''', (username, action, target_type, target_id, details))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_audit_db()
    app.run(port=5000, debug=True)
