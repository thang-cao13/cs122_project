# Expense Tracker Application

## Overview
This project is a personal expense tracking system that allows users to record, manage, and analyze their spending. It supports CRUD operations, search functionality, reporting, and receipt scanning using OCR.

---

## Features
- Add, view, edit, and delete expenses
- Search expenses by keyword
- Generate reports and charts
- Upload and scan receipts (OCR)
- QR code upload from phone

---

## Project Structure
expense_tracker_project/
├── app.py
├── database.py
├── expenses.db
├── requirements.txt
├── packages.txt
└── README.md

---

## Requirements
- Python 3.9+

Install dependencies:
pip install -r requirements.txt

---

## Tesseract OCR Setup (Required)
Mac:
brew install tesseract

---

## Run the Program
python3 -m streamlit run app.py

Open in browser:
http://localhost:8501

---

## Notes
- Database is created automatically
- OCR works best with clear images
- QR upload works best on deployed site

---

## Author
Kevin Cao
