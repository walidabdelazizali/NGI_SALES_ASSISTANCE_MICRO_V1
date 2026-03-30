# NGI_SALES_ASSISTANCE_MICRO_V1

A minimal, modular micro-system for insurance sales assistance and knowledge lookup. Supports:
- Training question lookup
- FAQ lookup
- Plan lookup
- Network lookup

## Folder Structure
```
NGI_SALES_ASSISTANCE_MICRO_V1/
├── README.md
├── requirements.txt
├── data/
│   ├── training_questions_master.csv
│   ├── plans/
│   │   └── .gitkeep
│   ├── networks/
│   │   └── .gitkeep
│   └── faq/
│       └── .gitkeep
├── scripts/
│   └── ask_kb.py
├── src/
│   ├── __init__.py
│   ├── kb_query.py
│   ├── training_qa_lookup.py
│   ├── plan_lookup.py
│   ├── network_lookup.py
│   ├── excel_loader.py
│   └── utils.py
└── tests/
    └── test_smoke.py
```

## How to Run

1. Install requirements (if any):
   ```
   pip install -r requirements.txt
   ```
2. Ask a question from the project root:
   ```
   python scripts/ask_kb.py "What is the annual limit for Remedy 02?"
   ```

## Example Commands
```
python scripts/ask_kb.py "What is the network for Remedy 02?"
python scripts/ask_kb.py "Show me the FAQ for direct billing."
python scripts/ask_kb.py "What is the plan copayment?"
```

## Notes
- Place your plan/network/FAQ data in the respective folders under `data/`.
- The system will first try training/FAQ lookup, then plan/network lookup.
- Code is modular and easy to extend.