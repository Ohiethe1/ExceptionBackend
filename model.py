# === model.py ===
from sklearn.pipeline import make_pipeline
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB

# Expanded training data for Exception Claim Form fields
TRAINING_DATA = [
    # Employee Name examples
    {"text": "John Doe", "label": "Employee Name"},
    {"text": "Jane Smith", "label": "Employee Name"},
    {"text": "Employee Name (please print)", "label": "Employee Name"},
    # Pass Number examples
    {"text": "12345678", "label": "Pass Number"},
    {"text": "Pass Number", "label": "Pass Number"},
    # Title examples
    {"text": "Operator", "label": "Title"},
    {"text": "Title", "label": "Title"},
    # RDOS examples
    {"text": "Sat/Sun", "label": "RDOS"},
    {"text": "RDOS", "label": "RDOS"},
    # Actual OT Date examples
    {"text": "2024-07-01", "label": "Actual OT Date"},
    {"text": "Actual OT Date", "label": "Actual OT Date"},
    # DIV examples
    {"text": "A", "label": "DIV"},
    {"text": "DIV", "label": "DIV"},
    # Comments
    {"text": "Comments:", "label": "Comments"},
    {"text": "Worked extra hours", "label": "Comments"},
    # Supervisor Name
    {"text": "Supv. Name (please print)", "label": "Supervisor Name"},
    {"text": "Jane Supervisor", "label": "Supervisor Name"},
    # Supervisor Pass No.
    {"text": "Pass No.", "label": "Supervisor Pass No."},
    {"text": "654321", "label": "Supervisor Pass No."},
    # OTO
    {"text": "OTO", "label": "OTO"},
    {"text": "YES", "label": "OTO"},
    {"text": "NO", "label": "OTO"},
    # OTO Amount Saved
    {"text": "OTO AMOUNT SAVED", "label": "OTO Amount Saved"},
    {"text": "2", "label": "OTO Amount Saved"},
    # Entered in UTS
    {"text": "Entered in UTS", "label": "Entered in UTS"},
    # Table fields (row data)
    {"text": "35", "label": "Exception Code"},
    {"text": "Extra Platform Assign.", "label": "Exception Code Description"},
    {"text": "Line/Location", "label": "Line/Location"},
    {"text": "Run No.", "label": "Run No."},
    {"text": "Exception Time", "label": "Exception Time"},
    {"text": "Overtime", "label": "Overtime"},
    {"text": "Bonus", "label": "Bonus"},
    {"text": "Nite Diff.", "label": "Nite Diff."},
    {"text": "TA Job No.", "label": "TA Job No."},
    # Add more as needed for your forms
]

def train_model():
    texts = [item["text"] for item in TRAINING_DATA]
    labels = [item["label"] for item in TRAINING_DATA]
    model = make_pipeline(CountVectorizer(), MultinomialNB())
    model.fit(texts, labels)
    return model

def predict_field(model, text_line):
    """Predict the field label for a given text line."""
    return model.predict([text_line])[0]