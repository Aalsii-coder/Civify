# Civify

**Data-Mismatch Detection and Human Review System for Digital Public Services**

Civify compares synthetic citizen and asset records, explains field-level differences, routes uncertain cases for human review, and stores reviewer decisions in a local SQLite audit log.

## What is included

- Case queue with search and triage filters
- Side-by-side citizen and asset records
- Field-level similarity and plain-language explanations
- Human review form
- Local SQLite audit log
- Overview and synthetic evaluation pages
- Unit tests for the matching rules

## Important scope

- The included records are fictional demo data.
- A similarity score is a signal for review, not proof of identity, fraud, or wrongdoing.
- Civify does not decide welfare eligibility.
- Evaluation results apply only to the included generated dataset. They are not production performance claims.
- This version does not connect to government databases, live monitoring feeds, or real identity systems.

## Run on Windows / VS Code

1. Extract the project folder.
2. Open that folder in VS Code.
3. Ensure Python is installed and available from the terminal.
4. Double-click `run_civify.bat`, or run these commands in the VS Code PowerShell terminal:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

5. Streamlit will print a local URL, usually `http://localhost:8501`. Open it in your browser.

The first run installs the required packages. You can also use `run_tests.bat` after setup.

## Run tests and evaluation

```powershell
.\.venv\Scripts\python.exe test_matching.py
.\.venv\Scripts\python.exe evaluate.py
```

The evaluation treats `Needs review` and `Insufficient data` as abstentions. Binary metrics are calculated only on cases receiving a decisive match/non-match result, and the report prints decision coverage separately.

## Project structure

```text
Civify/
├── app.py             # Streamlit interface and page logic
├── matching.py        # Field comparisons, score, triage, explanations
├── sample_data.py     # Repeatable fictional demo cases and labels
├── database.py        # Local SQLite review history
├── evaluate.py        # Evaluation metrics for generated cases
├── test_matching.py   # Unit tests for matching rules
├── requirements.txt   # Python dependencies
├── run_civify.bat     # Windows setup and launch helper
├── run_tests.bat      # Windows test/evaluation helper
├── .gitignore
└── README.md
```

`civify.db` is created automatically in the project folder when a review is saved. It is excluded from version control because it can contain reviewer notes.

## Matching logic

The current score combines available field similarities using these weights:

- Full name: 40%
- Date of birth: 35%
- Address: 25%

Missing fields are called out rather than treated as a perfect match. The current rules are deliberately small and readable so they can be inspected and changed in `matching.py`.

## Background reading

These sources provide context on concerns around large-scale welfare data matching and digital public-service systems:

- [Al Jazeera — How an algorithm denied food to thousands of poor in India's Telangana (24 January 2024)](https://www.aljazeera.com/economy/2024/1/24/how-an-algorithm-denied-food-thousands-of-poor-in-indias-telangana)
- [Amnesty International — Entity resolution in India's welfare digitalization (30 April 2024)](https://www.amnesty.org/en/latest/research/2024/04/entity-resolution-in-indias-welfare-digitalization/)
