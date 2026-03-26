import sqlite3


def create_table():
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

    conn.commit()
    conn.close()


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


def update_expense(id, expense_name, category, amount, date, payment_method, notes):
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE expenses
    SET expense_name = ?, category = ?, amount = ?, date = ?, payment_method = ?, notes = ?
    WHERE id = ?
    """, (expense_name, category, amount, date, payment_method, notes, id))

    conn.commit()
    conn.close()


def delete_expense(id):
    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM expenses WHERE id = ?", (id,))

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


create_table()