# === model.py ===
from sklearn.pipeline import make_pipeline
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB

def train_model():
    data = [
        {"text": "John Doe", "label": "Name"},
        {"text": "Jane Smith", "label": "Name"},
        {"text": "2025-07-19", "label": "Date"},
        {"text": "July 4, 2024", "label": "Date"},
        {"text": "123 Main St.", "label": "Address"},
        {"text": "456 Elm Ave", "label": "Address"},
    ]
    texts = [item["text"] for item in data]
    labels = [item["label"] for item in data]

    model = make_pipeline(CountVectorizer(), MultinomialNB())
    model.fit(texts, labels)
    return model