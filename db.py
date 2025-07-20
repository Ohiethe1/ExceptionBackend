# === db.py ===
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def add_user(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    try:
        hashed_pw = generate_password_hash(password)
        c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_pw))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def check_user(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT password FROM users WHERE username = ?', (username,))
    row = c.fetchone()
    conn.close()
    if row:
        return check_password_hash(row[0], password)
    return False

import sqlite3

def init_exception_form_db():
    conn = sqlite3.connect('forms.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS exception_forms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pass_number TEXT,
            title TEXT,
            employee_name TEXT,
            rdos TEXT,
            actual_ot_date TEXT,
            div TEXT,
            comments TEXT,
            supervisor_name TEXT,
            supervisor_pass_no TEXT,
            oto TEXT,
            oto_amount_saved TEXT,
            entered_in_uts TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS exception_form_rows (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            form_id INTEGER,
            code TEXT,
            code_description TEXT,
            line_location TEXT,
            run_no TEXT,
            exception_time_from_hh TEXT,
            exception_time_from_mm TEXT,
            exception_time_to_hh TEXT,
            exception_time_to_mm TEXT,
            overtime_hh TEXT,
            overtime_mm TEXT,
            bonus_hh TEXT,
            bonus_mm TEXT,
            nite_diff_hh TEXT,
            nite_diff_mm TEXT,
            ta_job_no TEXT,
            FOREIGN KEY(form_id) REFERENCES exception_forms(id)
        )
    ''')
    conn.commit()
    conn.close()

import re
from db import init_exception_form_db, store_exception_form
from exception_codes import exception_codes

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

def store_exception_form(form_data, rows):
    conn = sqlite3.connect('forms.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO exception_forms (
            pass_number, title, employee_name, rdos, actual_ot_date, div,
            comments, supervisor_name, supervisor_pass_no, oto, oto_amount_saved, entered_in_uts
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        form_data['pass_number'], form_data['title'], form_data['employee_name'],
        form_data['rdos'], form_data['actual_ot_date'], form_data['div'],
        form_data['comments'], form_data['supervisor_name'], form_data['supervisor_pass_no'],
        form_data['oto'], form_data['oto_amount_saved'], form_data['entered_in_uts']
    ))
    form_id = c.lastrowid
    for row in rows:
        c.execute('''
            INSERT INTO exception_form_rows (
                form_id, code, code_description, line_location, run_no,
                exception_time_from_hh, exception_time_from_mm,
                exception_time_to_hh, exception_time_to_mm,
                overtime_hh, overtime_mm, bonus_hh, bonus_mm,
                nite_diff_hh, nite_diff_mm, ta_job_no
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            form_id, row['code'], row['code_description'], row['line_location'], row['run_no'],
            row['exception_time_from_hh'], row['exception_time_from_mm'],
            row['exception_time_to_hh'], row['exception_time_to_mm'],
            row['overtime_hh'], row['overtime_mm'], row['bonus_hh'], row['bonus_mm'],
            row['nite_diff_hh'], row['nite_diff_mm'], row['ta_job_no']
        ))
    conn.commit()
    conn.close()