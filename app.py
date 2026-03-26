import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from database import add_expense, view_expenses, update_expense, delete_expense, search_expenses

st.title("Expense Tracker")

menu = [
    "Add Expense",
    "View Expenses",
    "Update Expense",
    "Delete Expense",
    "Search Expense",
    "Reports"
]

choice = st.sidebar.selectbox("Menu", menu)

# ADD
if choice == "Add Expense":
    st.subheader("Add New Expense")

    expense_name = st.text_input("Expense Name")
    category = st.text_input("Category")
    amount = st.number_input("Amount", min_value=0.0, format="%.2f")
    date = st.text_input("Date (YYYY-MM-DD)")
    payment_method = st.text_input("Payment Method")
    notes = st.text_area("Notes")

    if st.button("Add"):
        add_expense(expense_name, category, amount, date, payment_method, notes)
        st.success("Expense added!")

# VIEW
elif choice == "View Expenses":
    st.subheader("All Expenses")

    data = view_expenses()

    if data:
        df = pd.DataFrame(
            data,
            columns=["ID", "Expense Name", "Category", "Amount", "Date", "Payment Method", "Notes"]
        )
        st.dataframe(df)
    else:
        st.warning("No expenses found.")

# UPDATE
elif choice == "Update Expense":
    st.subheader("Update Expense")

    expense_id = st.number_input("Enter Expense ID to Update", min_value=1, step=1)
    new_name = st.text_input("New Expense Name")
    new_category = st.text_input("New Category")
    new_amount = st.number_input("New Amount", min_value=0.0, format="%.2f")
    new_date = st.text_input("New Date (YYYY-MM-DD)")
    new_payment = st.text_input("New Payment Method")
    new_notes = st.text_area("New Notes")

    if st.button("Update"):
        update_expense(
            expense_id,
            new_name,
            new_category,
            new_amount,
            new_date,
            new_payment,
            new_notes
        )
        st.success("Expense updated!")

# DELETE
elif choice == "Delete Expense":
    st.subheader("Delete Expense")

    expense_id = st.number_input("Enter Expense ID to Delete", min_value=1, step=1)

    if st.button("Delete"):
        delete_expense(expense_id)
        st.success("Expense deleted!")

# SEARCH
elif choice == "Search Expense":
    st.subheader("Search Expenses")

    keyword = st.text_input("Enter keyword")

    if st.button("Search"):
        results = search_expenses(keyword)

        if results:
            df = pd.DataFrame(
                results,
                columns=["ID", "Expense Name", "Category", "Amount", "Date", "Payment Method", "Notes"]
            )
            st.dataframe(df)
        else:
            st.warning("No matching expenses found.")

# REPORTS
elif choice == "Reports":
    st.subheader("Expense Reports")

    data = view_expenses()

    if data:
        df = pd.DataFrame(
            data,
            columns=["ID", "Expense Name", "Category", "Amount", "Date", "Payment Method", "Notes"]
        )

        st.write("### Total Spending")
        total_spending = df["Amount"].sum()
        st.write(f"${total_spending:.2f}")

        st.write("### Spending by Category")
        category_summary = df.groupby("Category")["Amount"].sum()
        st.dataframe(category_summary)

        fig, ax = plt.subplots()
        category_summary.plot(kind="bar", ax=ax)
        ax.set_ylabel("Amount")
        ax.set_title("Expenses by Category")
        st.pyplot(fig)

    else:
        st.warning("No expense data available.")