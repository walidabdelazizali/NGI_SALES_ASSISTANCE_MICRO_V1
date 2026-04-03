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
    if result["type"] is None:
        print("No answer found in training KB.")
    else:
        print(f"Type: {result['type']}")
        print("Result:")
        for k, v in result["result"].items():
            print(f"  {k}: {v}")

if __name__ == "__main__":
    main()
