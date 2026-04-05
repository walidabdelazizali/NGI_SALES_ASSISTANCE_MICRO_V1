import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent.parent / 'src'
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from training_qa_lookup import lookup_training_qa
from plan_lookup import lookup_plan
from network_lookup import lookup_network

DATA_DIR = Path(__file__).resolve().parent.parent / 'data'
TRAINING_QA_CSV = DATA_DIR / 'training_questions_master.csv'

def main():
    print("Owner Mode: Remedy 02 Q&A (type 'exit' to quit)")
    while True:
        try:
            question = input("Enter your question: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break
        if not question or question.lower() in {"exit", "quit"}:
            print("Exiting.")
            break
        # Plan
        if lookup_plan and lookup_network and lookup_training_qa:
            if any(word in question.lower() for word in ["remedy", "plan", "limit", "coverage", "deductible", "telemedicine", "wellness", "reimbursement", "maternity", "declaration", "copay", "network"]):
                plan_result = lookup_plan(question)
                if plan_result and plan_result.get('status') == 'found':
                    print(plan_result['answer'])
                    continue
            # Network
            net_result = lookup_network(question)
            if net_result and net_result.get('status') == 'found':
                print(net_result['answer'])
                continue
            # FAQ
            answer = lookup_training_qa(question, TRAINING_QA_CSV)
            if answer:
                print(answer)
                continue
        print("No answer found.")

if __name__ == "__main__":
    main()
