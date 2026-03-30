from utils import normalize_text

def answer_question(question, workbook_data):
    q = normalize_text(question)
    # Example: simple plan lookup
    for sheet, rows in workbook_data.items():
        for row in rows:
            if q in normalize_text(str(row)):
                return {'answer': str(row), 'status': 'ok'}
    return {'answer': 'No answer found.', 'status': 'not_found'}
