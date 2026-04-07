import streamlit as st
import pandas as pd
import plotly.express as px
import pytesseract
import re

from datetime import datetime
from PIL import Image, ImageOps, ImageFilter
from database import (
    add_expense,
    view_expenses,
    get_expense_by_id,
    update_expense,
    delete_expense,
    search_expenses,
)

pytesseract.pytesseract.tesseract_cmd = "/opt/homebrew/bin/tesseract"

st.set_page_config(
    page_title="Expense Tracker",
    page_icon="",
    layout="wide"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background: linear-gradient(180deg, #0b0f19 0%, #111827 100%);
    }

    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 2rem;
        padding-left: 2rem;
        padding-right: 2rem;
        max-width: 1400px;
    }

    section[data-testid="stSidebar"] {
        background: rgba(17, 24, 39, 0.95);
        border-right: 1px solid rgba(255,255,255,0.08);
    }

    section[data-testid="stSidebar"] .stRadio > div {
        gap: 0.35rem;
    }

    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] div {
        font-size: 0.97rem;
    }

    .hero-card {
        background: linear-gradient(135deg, rgba(255,255,255,0.06), rgba(255,255,255,0.03));
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 24px;
        padding: 1.4rem 1.5rem;
        margin-bottom: 1.25rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.20);
    }

    .hero-title {
        font-size: 2rem;
        font-weight: 700;
        letter-spacing: -0.02em;
        color: #f9fafb;
        margin-bottom: 0.3rem;
    }

    .hero-subtitle {
        color: #9ca3af;
        font-size: 1rem;
        margin-bottom: 0;
    }

    .section-card {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 22px;
        padding: 1.15rem;
        margin-bottom: 1rem;
        box-shadow: 0 8px 20px rgba(0,0,0,0.14);
    }

    .section-title {
        font-size: 1.05rem;
        font-weight: 600;
        color: #f3f4f6;
        margin-bottom: 0.8rem;
    }

    div[data-testid="stMetric"] {
        background: linear-gradient(180deg, #141b2d 0%, #111827 100%);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 20px;
        padding: 1rem;
        box-shadow: 0 8px 20px rgba(0,0,0,0.18);
    }

    div[data-testid="stMetric"] label {
        color: #9ca3af !important;
        font-weight: 600;
    }

    div[data-testid="stMetric"] > div {
        color: #f9fafb !important;
    }

    div[data-testid="stDataFrame"] {
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 18px;
        overflow: hidden;
    }

    .stButton > button {
        border-radius: 14px;
        height: 2.9rem;
        border: 1px solid rgba(255,255,255,0.08);
        background: linear-gradient(180deg, #f9fafb 0%, #e5e7eb 100%);
        color: #111827;
        font-weight: 600;
    }

    .stDownloadButton > button {
        border-radius: 14px;
        height: 2.9rem;
        border: 1px solid rgba(255,255,255,0.08);
        background: transparent;
        color: #f9fafb;
        font-weight: 600;
    }

    .stTextInput input,
    .stTextArea textarea,
    .stNumberInput input,
    .stDateInput input {
        border-radius: 14px !important;
    }

    .small-muted {
        color: #9ca3af;
        font-size: 0.92rem;
    }
</style>
""", unsafe_allow_html=True)

menu = [
    "Add Expense",
    "View Expenses",
    "Edit Expense",
    "Delete Expense",
    "Search Expense",
    "Scan Receipt",
    "Reports"
]

choice = st.sidebar.radio("Navigation", menu)

category_options = [
    "Food",
    "Transportation",
    "Bills",
    "Shopping",
    "Entertainment",
    "Health",
    "Other"
]

payment_options = [
    "Cash",
    "Debit Card",
    "Credit Card",
    "Online",
    "Other"
]


def render_header(title, subtitle):
    st.markdown(
        f"""
        <div class="hero-card">
            <div class="hero-title">{title}</div>
            <div class="hero-subtitle">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def section_start(title):
    st.markdown(f'<div class="section-card"><div class="section-title">{title}</div>', unsafe_allow_html=True)


def section_end():
    st.markdown("</div>", unsafe_allow_html=True)


def parse_date(date_string):
    return datetime.strptime(date_string, "%Y-%m-%d").date()


def make_label(expense):
    return f"{expense[1]} | {expense[2]} | {float(expense[3]):.2f} | {expense[4]}"


def load_dataframe():
    data = view_expenses()

    if not data:
        return pd.DataFrame(columns=["ID", "Name", "Category", "Amount", "Date", "Payment", "Notes"])

    df = pd.DataFrame(
        data,
        columns=["ID", "Name", "Category", "Amount", "Date", "Payment", "Notes"]
    )

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")
    return df


def guess_category(text):
    text = text.lower()

    keyword_map = {
        "Food": ["restaurant", "cafe", "coffee", "burger", "pizza", "ramen", "food", "ubereats", "doordash"],
        "Transportation": ["uber", "lyft", "shell", "chevron", "gas", "parking", "transit", "train"],
        "Bills": ["utility", "bill", "electric", "internet", "water", "xfinity", "pge"],
        "Shopping": ["amazon", "target", "walmart", "store", "shop"],
        "Entertainment": ["movie", "netflix", "spotify", "concert", "game"],
        "Health": ["pharmacy", "walgreens", "cvs", "clinic", "hospital", "health"],
    }

    for category, words in keyword_map.items():
        if any(word in text for word in words):
            return category

    return "Other"


def guess_payment_method(text):
    text = text.lower()

    if "visa" in text or "mastercard" in text or "credit" in text:
        return "Credit Card"
    if "debit" in text:
        return "Debit Card"
    if "cash" in text:
        return "Cash"
    if "paypal" in text or "apple pay" in text or "google pay" in text or "online" in text:
        return "Online"

    return "Other"


def preprocess_receipt_image(image):
    grayscale = ImageOps.grayscale(image)
    grayscale = ImageOps.autocontrast(grayscale)
    grayscale = grayscale.filter(ImageFilter.SHARPEN)
    return grayscale


def extract_receipt_text(image):
    processed = preprocess_receipt_image(image)
    return pytesseract.image_to_string(processed)


def parse_receipt_text(text):
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    merchant = "Receipt"

    ignored_words = [
        "receipt", "thank you", "subtotal", "total", "visa",
        "mastercard", "debit", "credit", "tax", "change", "cash"
    ]

    for line in lines:
        lower_line = line.lower()
        if len(line) > 2 and any(char.isalpha() for char in line):
            if not any(word in lower_line for word in ignored_words):
                merchant = line[:60]
                break

    date_patterns = [
        r"\b\d{4}-\d{2}-\d{2}\b",
        r"\b\d{2}/\d{2}/\d{4}\b",
        r"\b\d{2}/\d{2}/\d{2}\b",
        r"\b\d{2}-\d{2}-\d{4}\b"
    ]

    found_date = None
    for pattern in date_patterns:
        match = re.search(pattern, text)
        if match:
            found_date = match.group(0)
            break

    parsed_date = datetime.today().date()
    if found_date:
        for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%m/%d/%y", "%m-%d-%Y"):
            try:
                parsed_date = datetime.strptime(found_date, fmt).date()
                break
            except ValueError:
                pass

    amount_matches = re.findall(r"\d+\.\d{2}", text)
    amount = 0.0
    if amount_matches:
        try:
            amount = max(float(value) for value in amount_matches)
        except ValueError:
            amount = 0.0

    return {
        "expense_name": merchant,
        "category": guess_category(text),
        "amount": amount,
        "date": parsed_date,
        "payment_method": guess_payment_method(text),
        "notes": "Auto-filled from receipt scan",
        "raw_text": text
    }


def render_receipt_result(uploaded_file, source_name):
    try:
        image = Image.open(uploaded_file)
        st.image(image, caption=f"{source_name} preview", width=700)

        with st.spinner("Reading receipt..."):
            extracted_text = extract_receipt_text(image)
            parsed = parse_receipt_text(extracted_text)

        st.success("Receipt processed. Review and save the expense below.")

        with st.expander("Show OCR text"):
            st.text(parsed["raw_text"])

        col1, col2 = st.columns(2)

        with col1:
            expense_name = st.text_input(
                "Expense Name",
                value=parsed["expense_name"],
                key=f"{source_name}_expense_name"
            )
            category = st.selectbox(
                "Category",
                category_options,
                index=category_options.index(parsed["category"]) if parsed["category"] in category_options else len(category_options) - 1,
                key=f"{source_name}_category"
            )
            amount = st.number_input(
                "Amount",
                min_value=0.0,
                value=float(parsed["amount"]),
                format="%.2f",
                key=f"{source_name}_amount"
            )

        with col2:
            date = st.date_input(
                "Date",
                value=parsed["date"],
                key=f"{source_name}_date"
            )
            payment_method = st.selectbox(
                "Payment Method",
                payment_options,
                index=payment_options.index(parsed["payment_method"]) if parsed["payment_method"] in payment_options else len(payment_options) - 1,
                key=f"{source_name}_payment"
            )
            notes = st.text_area(
                "Notes",
                value=parsed["notes"],
                key=f"{source_name}_notes"
            )

        if st.button("Save Scanned Expense", use_container_width=True, key=f"{source_name}_save"):
            add_expense(
                expense_name,
                category,
                amount,
                str(date),
                payment_method,
                notes
            )
            st.success("Scanned expense saved.")
            st.rerun()

    except pytesseract.pytesseract.TesseractNotFoundError:
        st.error("Tesseract OCR is not installed in this environment.")
    except Exception as e:
        st.error(f"Could not process receipt: {e}")


if choice == "Add Expense":
    render_header("Expense Tracker", "Add a new expense with a cleaner, more structured form.")

    col1, col2 = st.columns(2)

    with col1:
        section_start("Expense Details")
        expense_name = st.text_input("Expense Name")
        category = st.selectbox("Category", category_options)
        amount = st.number_input("Amount", min_value=0.0, format="%.2f")
        section_end()

    with col2:
        section_start("Payment Details")
        date = st.date_input("Date")
        payment_method = st.selectbox("Payment Method", payment_options)
        notes = st.text_area("Notes")
        section_end()

    if st.button("Add Expense", use_container_width=True):
        add_expense(
            expense_name,
            category,
            amount,
            str(date),
            payment_method,
            notes
        )
        st.success("Expense added.")
        st.rerun()

elif choice == "View Expenses":
    render_header("All Expenses", "Browse your saved expenses and export them as a CSV file.")

    df = load_dataframe()

    if not df.empty:
        section_start("Expense Table")
        st.dataframe(df, use_container_width=True, height=460)
        section_end()

        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download CSV",
            csv,
            "expenses.csv",
            "text/csv",
            use_container_width=True
        )
    else:
        st.warning("No expenses found.")

elif choice == "Edit Expense":
    render_header("Edit Expense", "Find an expense by keyword and update its details.")

    keyword = st.text_input("Search for the expense you want to edit")

    if keyword:
        matches = search_expenses(keyword)

        if matches:
            match_df = pd.DataFrame(
                matches,
                columns=["ID", "Name", "Category", "Amount", "Date", "Payment", "Notes"]
            )

            section_start("Matching Expenses")
            st.dataframe(match_df, use_container_width=True, height=260)
            section_end()

            selected = st.selectbox(
                "Select expense to edit",
                matches,
                format_func=make_label
            )

            selected_expense = get_expense_by_id(selected[0])

            if selected_expense:
                current_id = selected_expense[0]
                current_name = selected_expense[1]
                current_category = selected_expense[2]
                current_amount = float(selected_expense[3])
                current_date = parse_date(selected_expense[4])
                current_payment = selected_expense[5]
                current_notes = selected_expense[6] or ""

                col1, col2 = st.columns(2)

                with col1:
                    section_start("Edit Main Details")
                    new_name = st.text_input("Expense Name", value=current_name)
                    new_category = st.selectbox(
                        "Category",
                        category_options,
                        index=category_options.index(current_category)
                    )
                    new_amount = st.number_input(
                        "Amount",
                        value=current_amount,
                        min_value=0.0,
                        format="%.2f"
                    )
                    section_end()

                with col2:
                    section_start("Edit Payment Details")
                    new_date = st.date_input("Date", value=current_date)
                    new_payment = st.selectbox(
                        "Payment Method",
                        payment_options,
                        index=payment_options.index(current_payment)
                    )
                    new_notes = st.text_area("Notes", value=current_notes)
                    section_end()

                if st.button("Save Changes", use_container_width=True):
                    update_expense(
                        current_id,
                        new_name,
                        new_category,
                        new_amount,
                        str(new_date),
                        new_payment,
                        new_notes
                    )
                    st.success("Expense updated.")
                    st.rerun()
        else:
            st.warning("No matching expenses found.")
    else:
        st.info("Enter a keyword like expense name, category, payment method, or notes.")

elif choice == "Delete Expense":
    render_header("Delete Expense", "Select an expense record and remove it from the database.")

    df = load_dataframe()

    if not df.empty:
        section_start("Current Expenses")
        st.dataframe(df[["ID", "Name", "Category", "Amount", "Date"]], use_container_width=True, height=320)
        section_end()

        data = view_expenses()
        selected = st.selectbox(
            "Select expense to delete",
            data,
            format_func=make_label
        )

        if st.button("Delete Expense", use_container_width=True):
            delete_expense(selected[0])
            st.success("Expense deleted.")
            st.rerun()
    else:
        st.warning("No expenses found.")

elif choice == "Search Expense":
    render_header("Search Expense", "Search by keyword across name, category, payment method, and notes.")

    keyword = st.text_input("Keyword")

    if st.button("Search", use_container_width=True):
        results = search_expenses(keyword)

        if results:
            df = pd.DataFrame(
                results,
                columns=["ID", "Name", "Category", "Amount", "Date", "Payment", "Notes"]
            )
            section_start("Search Results")
            st.dataframe(df, use_container_width=True, height=360)
            section_end()
        else:
            st.warning("No matching expenses found.")

elif choice == "Scan Receipt":
    render_header("Scan Receipt", "Upload a receipt image and let the app auto-fill the expense form.")

    uploaded_receipt = st.file_uploader(
        "Upload receipt image",
        type=["png", "jpg", "jpeg"],
        key="desktop_receipt_upload"
    )

    if uploaded_receipt is not None:
        render_receipt_result(uploaded_receipt, "desktop_upload")

elif choice == "Reports":
    render_header("Reports", "Explore trends, categories, payment patterns, and summary insights.")

    df = load_dataframe()

    if not df.empty:
        section_start("Filters")
        filter_col1, filter_col2, filter_col3 = st.columns(3)

        with filter_col1:
            min_date = df["Date"].min().date()
            max_date = df["Date"].max().date()
            date_range = st.date_input(
                "Date Range",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date
            )

        with filter_col2:
            selected_categories = st.multiselect(
                "Categories",
                options=sorted(df["Category"].dropna().unique().tolist()),
                default=sorted(df["Category"].dropna().unique().tolist())
            )

        with filter_col3:
            selected_payments = st.multiselect(
                "Payment Methods",
                options=sorted(df["Payment"].dropna().unique().tolist()),
                default=sorted(df["Payment"].dropna().unique().tolist())
            )
        section_end()

        filtered_df = df.copy()

        if isinstance(date_range, tuple) and len(date_range) == 2:
            start_date, end_date = date_range
            filtered_df = filtered_df[
                (filtered_df["Date"].dt.date >= start_date) &
                (filtered_df["Date"].dt.date <= end_date)
            ]

        if selected_categories:
            filtered_df = filtered_df[filtered_df["Category"].isin(selected_categories)]

        if selected_payments:
            filtered_df = filtered_df[filtered_df["Payment"].isin(selected_payments)]

        if filtered_df.empty:
            st.warning("No data matches your filters.")
        else:
            total_spending = filtered_df["Amount"].sum()
            total_transactions = len(filtered_df)
            average_expense = filtered_df["Amount"].mean()
            top_category = filtered_df.groupby("Category")["Amount"].sum().idxmax()

            kpi1, kpi2, kpi3, kpi4 = st.columns(4)
            kpi1.metric("Total Spending", f"{total_spending:,.2f}")
            kpi2.metric("Transactions", f"{total_transactions}")
            kpi3.metric("Average Expense", f"{average_expense:,.2f}")
            kpi4.metric("Top Category", top_category)

            section_start("Visualization Options")
            chart_col1, chart_col2 = st.columns(2)

            with chart_col1:
                chart_type = st.selectbox(
                    "Chart Type",
                    ["Bar Chart", "Pie Chart", "Line Chart"]
                )

            with chart_col2:
                analysis_view = st.selectbox(
                    "Analyze By",
                    ["Category", "Payment Method", "Month"]
                )
            section_end()

            if analysis_view == "Category":
                chart_data = (
                    filtered_df.groupby("Category", as_index=False)["Amount"]
                    .sum()
                    .sort_values("Amount", ascending=False)
                )
                x_col = "Category"
                title = "Spending by Category"

            elif analysis_view == "Payment Method":
                chart_data = (
                    filtered_df.groupby("Payment", as_index=False)["Amount"]
                    .sum()
                    .sort_values("Amount", ascending=False)
                )
                x_col = "Payment"
                title = "Spending by Payment Method"

            else:
                month_df = filtered_df.copy()
                month_df["Month"] = month_df["Date"].dt.to_period("M").astype(str)
                chart_data = (
                    month_df.groupby("Month", as_index=False)["Amount"]
                    .sum()
                    .sort_values("Month")
                )
                x_col = "Month"
                title = "Monthly Spending Trend"

            if chart_type == "Bar Chart":
                fig = px.bar(
                    chart_data,
                    x=x_col,
                    y="Amount",
                    title=title,
                    text_auto=".2f"
                )
            elif chart_type == "Pie Chart":
                fig = px.pie(
                    chart_data,
                    names=x_col,
                    values="Amount",
                    title=title
                )
            else:
                fig = px.line(
                    chart_data,
                    x=x_col,
                    y="Amount",
                    title=title,
                    markers=True
                )

            section_start("Chart")
            st.plotly_chart(fig, use_container_width=True)
            section_end()

            tab1, tab2, tab3 = st.tabs(["Filtered Data", "Category Summary", "Payment Summary"])

            with tab1:
                st.dataframe(filtered_df, use_container_width=True, height=320)

            with tab2:
                category_summary = (
                    filtered_df.groupby("Category")["Amount"]
                    .agg(["sum", "mean", "count"])
                    .reset_index()
                )
                category_summary.columns = ["Category", "Total", "Average", "Count"]
                st.dataframe(category_summary, use_container_width=True)

            with tab3:
                payment_summary = (
                    filtered_df.groupby("Payment")["Amount"]
                    .agg(["sum", "mean", "count"])
                    .reset_index()
                )
                payment_summary.columns = ["Payment Method", "Total", "Average", "Count"]
                st.dataframe(payment_summary, use_container_width=True)
    else:
        st.warning("No data available.")