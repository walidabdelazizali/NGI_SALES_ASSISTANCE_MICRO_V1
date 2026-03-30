def normalize_text(text):
    if not isinstance(text, str):
        return ""
    return text.strip().lower()
