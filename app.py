import streamlit as st
import pandas as pd
import plotly.express as px
import qrcode
import pytesseract
import re
import uuid

from io import BytesIO
from datetime import datetime
from PIL import Image, ImageOps, ImageFilter
from database import (
    add_expense,
    view_expenses,
    get_expense_by_id,
    update_expense,
    delete_expense,
    search_expenses,
    save_receipt_upload,
    get_receipt_upload_by_token,
)

pytesseract.pytesseract.tesseract_cmd = "/opt/homebrew/bin/tesseract"

st.set_page_config(page_title="Expense Tracker Dashboard", page_icon="💰", layout="wide")

APP_URL = "https://cs122project-abud3w8vhbshdczjzvnftw.streamlit.app/"

st.markdown("""
    <style>
    .main {
        padding-top: 1rem;
    }

    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 1.5rem;
        padding-left: 2rem;
        padding-right: 2rem;
    }

    section[data-testid="stSidebar"] {
        border-right: 1px solid rgba(255,255,255,0.08);
    }

    div[data-testid="stMetric"] {
        background: #111827;
        border: 1px solid #374151;
        border-radius: 16px;
        padding: 18px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
    }

    div[data-testid="stMetric"] label {
        color: #d1d5db !important;
        font-weight: 600;
    }

    div[data-testid="stMetric"] div {
        color: white !important;
    }

    .small-note {
        color: #9ca3af;
        font-size: 0.92rem;
    }
    </style>
""", unsafe_allow_html=True)

query_params = st.query_params
phone_upload_token = str(query_params.get("phone_upload", ""))

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

if "desktop_upload_token" not in st.session_state:
    st.session_state.desktop_upload_token = None


def parse_date(date_string):
    return datetime.strptime(date_string, "%Y-%m-%d").date()


def make_label(expense):
    return f"{expense[1]} | {expense[2]} | ${float(expense[3]):.2f} | {expense[4]}"


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


def generate_qr_code_bytes(url):
    qr = qrcode.QRCode(box_size=8, border=2)
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer.getvalue()


def render_receipt_result_from_pil(image, source_name):
    try:
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
            st.success("Scanned expense saved!")
            st.rerun()

    except pytesseract.pytesseract.TesseractNotFoundError:
        st.error("Tesseract OCR is not installed in this environment.")
    except Exception as e:
        st.error(f"Could not process receipt: {e}")


def render_receipt_result_from_upload(uploaded_file, source_name):
    image = Image.open(uploaded_file)
    render_receipt_result_from_pil(image, source_name)


if phone_upload_token:
    st.title("📱 Upload Receipt From Phone")
    st.caption("Take a receipt photo on your phone and send it back to your desktop session.")

    st.info("Allow camera permission, take the picture, then submit it. After that, refresh the desktop page.")

    camera_receipt = st.camera_input("Take receipt photo", key="phone_camera_capture")

    if camera_receipt is not None:
        image_bytes = camera_receipt.getvalue()
        save_receipt_upload(
            phone_upload_token,
            image_bytes,
            "phone_camera.jpg",
            "image/jpeg"
        )
        st.success("Receipt uploaded successfully. Return to your desktop and click 'Check for uploaded receipt'.")

    uploaded_receipt = st.file_uploader(
        "Or upload a receipt image from your phone",
        type=["png", "jpg", "jpeg"],
        key="phone_file_upload"
    )

    if uploaded_receipt is not None:
        save_receipt_upload(
            phone_upload_token,
            uploaded_receipt.getvalue(),
            uploaded_receipt.name,
            uploaded_receipt.type or "image/jpeg"
        )
        st.success("Receipt uploaded successfully. Return to your desktop and click 'Check for uploaded receipt'.")

else:
    st.title("Expense Tracker Dashboard")
    st.caption("Track, edit, analyze, and visualize your expenses")

    menu = [
        "Add Expense",
        "View Expenses",
        "Edit Expense",
        "Delete Expense",
        "Search Expense",
        "Scan Receipt",
        "Reports"
    ]

    choice = st.sidebar.radio("Menu", menu)

    if choice == "Add Expense":
        st.subheader("Add New Expense")

        col1, col2 = st.columns(2)

        with col1:
            expense_name = st.text_input("Expense Name")
            category = st.selectbox("Category", category_options)
            amount = st.number_input("Amount", min_value=0.0, format="%.2f")

        with col2:
            date = st.date_input("Date")
            payment_method = st.selectbox("Payment Method", payment_options)
            notes = st.text_area("Notes")

        if st.button("Add Expense", use_container_width=True):
            add_expense(
                expense_name,
                category,
                amount,
                str(date),
                payment_method,
                notes
            )
            st.success("Expense added!")
            st.rerun()

    elif choice == "View Expenses":
        st.subheader("All Expenses")

        df = load_dataframe()

        if not df.empty:
            st.dataframe(df, use_container_width=True)

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
        st.subheader("Edit Expense")

        keyword = st.text_input("Search for the expense you want to edit")

        if keyword:
            matches = search_expenses(keyword)

            if matches:
                match_df = pd.DataFrame(
                    matches,
                    columns=["ID", "Name", "Category", "Amount", "Date", "Payment", "Notes"]
                )
                st.dataframe(match_df, use_container_width=True)

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

                    with col2:
                        new_date = st.date_input("Date", value=current_date)
                        new_payment = st.selectbox(
                            "Payment Method",
                            payment_options,
                            index=payment_options.index(current_payment)
                        )
                        new_notes = st.text_area("Notes", value=current_notes)

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
                        st.success("Expense updated!")
                        st.rerun()
            else:
                st.warning("No matching expenses found.")
        else:
            st.info("Enter a keyword like expense name, category, payment method, or notes.")

    elif choice == "Delete Expense":
        st.subheader("Delete Expense")

        df = load_dataframe()

        if not df.empty:
            st.dataframe(df[["ID", "Name", "Category", "Amount", "Date"]], use_container_width=True)

            data = view_expenses()
            selected = st.selectbox(
                "Select expense to delete",
                data,
                format_func=make_label
            )

            if st.button("Delete Expense", use_container_width=True):
                delete_expense(selected[0])
                st.success("Expense deleted!")
                st.rerun()
        else:
            st.warning("No expenses found.")

    elif choice == "Search Expense":
        st.subheader("Search Expense")

        keyword = st.text_input("Keyword")

        if st.button("Search", use_container_width=True):
            results = search_expenses(keyword)

            if results:
                df = pd.DataFrame(
                    results,
                    columns=["ID", "Name", "Category", "Amount", "Date", "Payment", "Notes"]
                )
                st.dataframe(df, use_container_width=True)
            else:
                st.warning("No matching expenses found.")

    elif choice == "Scan Receipt":
        st.subheader("Scan Receipt")

        col1, col2 = st.columns([1, 1])

        with col1:
            st.write("### Upload From This Device")
            uploaded_receipt = st.file_uploader(
                "Upload receipt image",
                type=["png", "jpg", "jpeg"],
                key="desktop_receipt_upload"
            )

            if uploaded_receipt is not None:
                render_receipt_result_from_upload(uploaded_receipt, "desktop_upload")

        with col2:
            st.write("### Upload by Scanning From Phone")

            if st.button("Generate QR Code", use_container_width=True):
                st.session_state.desktop_upload_token = str(uuid.uuid4())

            token = st.session_state.desktop_upload_token

            if token:
                phone_upload_url = f"{APP_URL}?phone_upload={token}"
                qr_bytes = generate_qr_code_bytes(phone_upload_url)

                st.write("1. Scan the QR code with your phone")
                st.write("2. Your phone opens the camera upload page")
                st.write("3. Take the receipt picture on your phone")
                st.write("4. Submit it on your phone")
                st.write("5. Click the button below on your desktop")

                st.image(qr_bytes, caption=phone_upload_url, width=280)
                st.code(phone_upload_url)

                if st.button("Check for uploaded receipt", use_container_width=True):
                    uploaded_row = get_receipt_upload_by_token(token)

                    if uploaded_row:
                        image_bytes = uploaded_row[1]
                        image = Image.open(BytesIO(image_bytes))
                        st.success("Receipt received from phone.")
                        render_receipt_result_from_pil(image, "phone_transfer")
                    else:
                        st.warning("No receipt uploaded yet. Upload from your phone first.")
            else:
                st.info("Click 'Generate QR Code' to start the phone upload flow.")

    elif choice == "Reports":
        st.subheader("Interactive Reports")

        df = load_dataframe()

        if not df.empty:
            st.markdown("## Filters")

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
                st.markdown("## Summary")

                total_spending = filtered_df["Amount"].sum()
                total_transactions = len(filtered_df)
                average_expense = filtered_df["Amount"].mean()
                top_category = filtered_df.groupby("Category")["Amount"].sum().idxmax()

                kpi1, kpi2, kpi3, kpi4 = st.columns(4)
                kpi1.metric("Total Spending", f"${total_spending:,.2f}")
                kpi2.metric("Transactions", f"{total_transactions}")
                kpi3.metric("Average Expense", f"${average_expense:,.2f}")
                kpi4.metric("Top Category", top_category)

                st.markdown("## Visualizations")

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
                    fig.update_layout(xaxis_title=x_col, yaxis_title="Amount")

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
                    fig.update_layout(xaxis_title=x_col, yaxis_title="Amount")

                st.plotly_chart(fig, use_container_width=True)

                tab1, tab2, tab3 = st.tabs(["Filtered Data", "Category Summary", "Payment Summary"])

                with tab1:
                    st.dataframe(filtered_df, use_container_width=True)

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