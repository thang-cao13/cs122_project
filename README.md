## Expense Tracker Application

## Overview

The Expense Tracker Application is a data-driven system designed to help users record, manage, and analyze personal expenses. The system provides core database functionalities including adding, viewing, updating, deleting, and searching expenses, along with data visualization and receipt scanning using OCR.

# Features
* Add new expenses with category, amount, date, and payment method
* View all stored expenses in a structured table
* Edit and update existing expense records
* Delete expenses from the system
* Search expenses using keywords
* Generate reports and visualizations
* Upload and scan receipts using OCR
* QR code-based receipt upload from mobile devices

# Project Structure

expense_tracker_project/
│
├── app.py                # Main Streamlit application
├── database.py           # Database logic and schema
├── expenses.db           # SQLite database (auto-created)
├── requirements.txt      # Python dependencies
├── packages.txt          # System dependencies (for deployment)
└── README.md             # Project documentation

# Requirement

Python Version
* Python 3.9 or higher

Python Libraries

Install dependencies using:
```bash
pip install -r requirements.txt
```

Dependencies include:

* streamlit
* pandas
* plotly
* pillow
* pytesseract
* qrcode

# System Dependencies

Tesseract OCR (Required for receipt scanning)

Mac (Homebrew):
```bash
brew install tesseract
```

verify installtion:
```bash
tesseract --version
```

# Running the Application

Step 1: Navigate to project folder
```bash
cd expense_tracker_project
```

Step 2: Run the application
```bash
python3 -m streamlit run app.py
```

Step 3: Open in browser
```bash
http://localhost:8501
```

## Using the Application

# Add Expense

Enter expense details and click “Add Expense” to save.

# View Expenses

Displays all stored expense records.

# Edit Expense

Search by keyword, select a record, and update fields.

# Delete Expense

Select an expense and remove it from the database.

# Search Expense

Search expenses by name, category, or keywords.

# Scan Receipt

* Upload an image of a receipt
* System extracts text using OCR
* Auto-fills expense form

# QR Code Upload (Advanced Feature)

* Generate QR code on desktop
* Scan using phone
* Upload receipt image from phone
* Retrieve image on desktop

⸻

Notes

* The SQLite database (expenses.db) is created automatically on first run
* OCR accuracy depends on image quality
* QR upload feature works best using the deployed version of the app

⸻

Troubleshooting

Tesseract not found

Ensure path is set in app.py:
```py
pytesseract.pytesseract.tesseract_cmd = "/opt/homebrew/bin/tesseract"
```

Module not found errors

Run:
```bash
pip install -r requirements.txt
```

Data Source

* Data is user-generated through the application
* No external dataset is required

# Author

Kevin Cao, Nyi Tunn

# License

This project is for academic purposes only.
