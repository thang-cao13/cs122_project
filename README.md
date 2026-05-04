##Expense Tracker Application

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



