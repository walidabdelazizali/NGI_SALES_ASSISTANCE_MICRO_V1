import csv
import unicodedata
import re

def robust_normalize(text):
    if not isinstance(text, str):
        return ""
    text = text.translate(str.maketrans('٠١٢٣٤٥٦٧٨٩', '0123456789'))
    text = ''.join(c for c in unicodedata.normalize('NFKD', text) if not unicodedata.combining(c))
    text = text.lower().strip()
    text = re.sub(r'[^\w\s\u0600-\u06FF]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text

def lookup_training_qa(question, csv_path):
    q = robust_normalize(question)
    with open(csv_path, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if robust_normalize(row.get('question', '')) == q:
                return row.get('answer', '')
    return None
