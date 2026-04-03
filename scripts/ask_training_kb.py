import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from training_router import route_training_query

def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/ask_training_kb.py <your question>")
        sys.exit(1)
    query = " ".join(sys.argv[1:])
    result = route_training_query(query)
    print(f"Question: {query}\n")
    if result["type"] is None or not result["result"]:
        print("No clear training answer found.\nTry rephrasing the question with issue type, benefit name, or workflow context.")
        return

    type_map = {
        "faq": "FAQ",
        "rule": "RULE",
        "glossary": "GLOSSARY",
        "escalation": "ESCALATION"
    }
    type_label = type_map.get(result["type"], result["type"].upper())
    print("Best Match Type:")
    print(type_label + "\n")

    # Main answer field selection
    main_answer = None
    if result["type"] == "faq":
        main_answer = result["result"].get("answer", "")
    elif result["type"] == "rule":
        main_answer = result["result"].get("answer", "")
    elif result["type"] == "glossary":
        main_answer = result["result"].get("definition", "")
    elif result["type"] == "escalation":
        main_answer = result["result"].get("action", "")
    else:
        main_answer = ""
    print("Answer:\n")
    print(main_answer.strip() if main_answer else "(No answer text found)")

    # Supporting notes
    notes_fields = [
        "question", "rule_name", "term", "case_name", "owner", "category", "sub_category", "notes"
    ]
    notes = []
    for field in notes_fields:
        val = result["result"].get(field)
        if val:
            notes.append(f"* {field}: {val}")
    if notes:
        print("\nSupporting Notes:\n")
        for n in notes:
            print(n)

    # Record ID
    rec_id = result["result"].get("id") or result["result"].get("ID")
    if rec_id:
        print(f"\nRecord ID: {rec_id}")
    else:
        print("\nRecord ID: (unknown)")

if __name__ == "__main__":
    main()
