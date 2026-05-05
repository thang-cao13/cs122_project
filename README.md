# Expense Tracker Application

## Overview
The Expense Tracker Application is a data-driven system designed to help users record, manage, and analyze personal expenses. The system integrates a structured relational database with an interactive interface, enabling efficient storage, retrieval, and visualization of financial data. It provides users with a centralized platform to track spending patterns and gain insights into their financial habits.

---

## Features
- Add new expenses with category, amount, date, and payment method  
- View all stored expenses in a structured table format  
- Edit and update existing expense records  
- Delete expenses from the system  
- Search expenses using keywords  
- Generate interactive reports and visualizations  
- Upload and scan receipts using OCR (Tesseract)  
- QR code-based receipt upload from mobile devices  

---

## Project Structure
```
expense_tracker_project/
├── app.py              # Main Streamlit application
├── database.py         # Database logic and schema
├── expenses.db         # SQLite database (auto-created)
├── requirements.txt    # Python dependencies
├── packages.txt        # System dependencies (for deployment)
└── README.md           # Project documentation
```

---

## Requirements

### Python Version
- Python 3.9 or higher  

### Python Libraries
Install required dependencies:
pip install -r requirements.txt

Libraries used:
- streamlit  
- pandas  
- plotly  
- pillow  
- pytesseract  
- qrcode  
- numpy (<2 for compatibility)  

---

## System Dependencies

### Tesseract OCR (Required for Receipt Scanning)

Mac:
brew install tesseract

Verify installation:
tesseract --version

---

## Running the Application

### Step 1: Navigate to Project Folder
cd expense_tracker_project

### Step 2: Run the Application
python3 -m streamlit run app.py

### Step 3: Open in Browser
http://localhost:8501

---

## Application Usage

### Add Expense
Enter expense details including name, category, amount, date, and payment method, then click “Add Expense” to save.

### View Expenses
Displays all stored expenses in a table format. Users can scroll and review all entries.

### Edit Expense
Search for an expense using keywords, select a record, and update its details.

### Delete Expense
Select an expense record and remove it from the database.

### Search Expense
Search for expenses based on name, category, payment method, or notes.

### Reports
Generate visualizations such as:
- Spending by category  
- Payment method breakdown  
- Monthly spending trends  

### Scan Receipt (OCR)
- Upload an image of a receipt  
- System extracts text using Tesseract OCR  
- Automatically fills expense form fields  
- User can review and save the data  

### QR Code Upload (Advanced Feature)
- Generate a QR code on the desktop application  
- Scan the QR code using a mobile device  
- Upload a receipt image from the phone  
- Retrieve the image on the desktop application  

---

## Notes
- The SQLite database (`expenses.db`) is created automatically on first run  
- OCR accuracy depends on image clarity and lighting conditions  
- QR upload feature works best using the deployed version of the application  
- Ensure Tesseract is properly installed for OCR functionality  

---

## Troubleshooting

### Tesseract Not Found
Ensure the correct path is set in `app.py`:
pytesseract.pytesseract.tesseract_cmd = "/opt/homebrew/bin/tesseract"

Or use automatic detection:
import shutil
pytesseract.pytesseract.tesseract_cmd = shutil.which("tesseract")

### Module Errors
Reinstall dependencies:
pip install -r requirements.txt

### NumPy Compatibility Issue
Ensure the following line exists in requirements.txt:
numpy<2

---

## Data Source
All data used in this application is user-generated. No external datasets are required.

---

## Author
Thang Cao, Nyi Tun 

---

## License
This project is intended for academic use only.
