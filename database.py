import sqlite3


def create_tables():
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        expense_name TEXT NOT NULL,
        category TEXT NOT NULL,
        amount REAL NOT NULL,
        date TEXT NOT NULL,
        payment_method TEXT,
        notes TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS receipt_uploads (
        token TEXT PRIMARY KEY,
        image_data BLOB NOT NULL,
        filename TEXT,
        mime_type TEXT,
        uploaded_at TEXT DEFAULT CURRENT_TIMESTAMP,
        is_processed INTEGER DEFAULT 0
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS budgets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        month TEXT NOT NULL,
        category TEXT NOT NULL,
        budget_amount REAL NOT NULL,
        UNIQUE(month, category)
    )
    """)

    conn.commit()
    conn.close()


def set_budget(month, category, budget_amount):
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO budgets (month, category, budget_amount)
    VALUES (?, ?, ?)
    ON CONFLICT(month, category) DO UPDATE SET budget_amount = excluded.budget_amount
    """, (month, category, budget_amount))

    conn.commit()
    conn.close()


def get_budgets_for_month(month):
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()

    cursor.execute("SELECT category, budget_amount FROM budgets WHERE month = ?", (month,))
    rows = cursor.fetchall()

    conn.close()
    return {row[0]: row[1] for row in rows}


def add_expense(expense_name, category, amount, date, payment_method, notes):
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO expenses (expense_name, category, amount, date, payment_method, notes)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (expense_name, category, amount, date, payment_method, notes))

    conn.commit()
    conn.close()


def view_expenses():
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM expenses")
    rows = cursor.fetchall()

    conn.close()
    return rows


def get_expense_by_id(expense_id):
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM expenses WHERE id = ?", (expense_id,))
    row = cursor.fetchone()

    conn.close()
    return row


def update_expense(expense_id, expense_name, category, amount, date, payment_method, notes):
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE expenses
    SET expense_name = ?, category = ?, amount = ?, date = ?, payment_method = ?, notes = ?
    WHERE id = ?
    """, (expense_name, category, amount, date, payment_method, notes, expense_id))

    conn.commit()
    conn.close()


def delete_expense(expense_id):
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))

    conn.commit()
    conn.close()


def search_expenses(keyword):
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT * FROM expenses
    WHERE expense_name LIKE ? OR category LIKE ? OR payment_method LIKE ? OR notes LIKE ?
    """, (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"))

    rows = cursor.fetchall()

    conn.close()
    return rows


def save_receipt_upload(token, image_data, filename, mime_type):
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()

    cursor.execute("""
    INSERT OR REPLACE INTO receipt_uploads (token, image_data, filename, mime_type, is_processed)
    VALUES (?, ?, ?, ?, 0)
    """, (token, image_data, filename, mime_type))

    conn.commit()
    conn.close()


def get_receipt_upload_by_token(token):
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT token, image_data, filename, mime_type, uploaded_at, is_processed
    FROM receipt_uploads
    WHERE token = ?
    """, (token,))
    row = cursor.fetchone()

    conn.close()
    return row


create_tables()
