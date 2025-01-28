import streamlit as st
import pytesseract
from PIL import Image
import pandas as pd
from transformers import BertTokenizer, BertForSequenceClassification
from torch.nn.functional import softmax
import torch
import matplotlib.pyplot as plt
import re
import pymysql
from datetime import datetime

# Database connection
def create_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="sql777save##",
        database="supervised"
    )

# Transform date to YYYY-MM-DD format
def transform_date(date_str):
    try:
        current_year = datetime.now().year
        date_obj = datetime.strptime(f"{date_str}/{current_year}", "%m/%d/%Y")
        return date_obj.strftime("%Y-%m-%d")
    except ValueError:
        return None  # Return None if date is invalid

# Save data to MySQL database
def save_to_database(df, table_name="supervised.bank_statement"):
    try:
        connection = create_connection()
        cursor = connection.cursor()

        # Drop rows where 'DATE' is null
        df = df.dropna(subset=["DATE"])

        if df.empty:
            st.warning("No valid transactions to save. Please check the extracted dates.")
            return

        for index, row in df.iterrows():
            withdrawal = row['WITHDRAWAL'] if pd.notna(row['WITHDRAWAL']) else None
            deposit = row['DEPOSIT'] if pd.notna(row['DEPOSIT']) else None
            balance = row['BALANCE'] if pd.notna(row['BALANCE']) else None
            description = row['DESCRIPTION'] if 'DESCRIPTION' in row else 'No Description'
            category = row['CATEGORY'] if 'CATEGORY' in row else 'Uncategorized'

            cursor.execute(f"""
                INSERT INTO {table_name} (date, description, withdrawal, deposit, balance, category)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                row['DATE'], 
                description, 
                withdrawal, 
                deposit, 
                balance, 
                category
            ))

        connection.commit()
        st.success(f"Data saved to the '{table_name}' table successfully!")
    except Exception as e:
        st.error(f"Error saving data to the database: {e}")
    finally:
        if connection:
            connection.close()

# Extract transactions from OCR text
def extract_transactions(ocr_text):
    date_pattern = r'^\d{2}/\d{2}$'
    lines = ocr_text.splitlines()
    transactions = []

    for line in lines:
        parts = line.split()
        if parts and re.match(date_pattern, parts[0]):  # Check for valid date
            date = parts[0]
            balance = parts[-1]
            withdrawal, deposit = "", ""
            try:
                value = float(parts[-2].replace(",", ""))
                if "Deposit" in line or "Payment from" in line:
                    deposit = parts[-2]
                else:
                    withdrawal = parts[-2]
            except ValueError:
                pass

            description = " ".join(parts[1:-2])
            transactions.append([date, description, withdrawal, deposit, balance])

    return transactions

# Categorize transactions
def categorize_transactions(df):
    categories_keywords = {
        "Payment": ["payment", "Payment from Nala Spencer", "Payment from Kyubi Tayler"],
        "Bills": ["bill", "electricity", "gas", "water", "internet", "phone", "rent", "Phone Bill", "Electric Bill", "Rent Bill", "Internet Bill"],
        "Deposit": ["deposit", "Deposit"],
        "Tax": ["tax", "Withholding Tax"],
        "Expense": ["photography", "equipment", "payroll", "tools", "Picture Perfect Equipments", "Photography Tools Warehouse"],
        "Interest": ["interest", "Interest Earned"],
        "Salary": ["Payroll Run", "salary"]
    }

    def categorize(description):
        for category, keywords in categories_keywords.items():
            if any(keyword.lower() in description.lower() for keyword in keywords):
                return category
        return "Uncategorized"

    df["CATEGORY"] = df["DESCRIPTION"].apply(categorize)
    return df

# Display pie and bar charts
def show_charts(df):
    df["WITHDRAWAL"] = pd.to_numeric(df["WITHDRAWAL"], errors='coerce').fillna(0)
    df["DEPOSIT"] = pd.to_numeric(df["DEPOSIT"], errors='coerce').fillna(0)
    df["TOTAL_AMOUNT"] = df["WITHDRAWAL"] + df["DEPOSIT"]

    # Pie chart
    category_counts = df["CATEGORY"].value_counts()
    plt.figure(figsize=(8, 8))
    plt.pie(category_counts, labels=category_counts.index, autopct="%1.1f%%", startangle=140, colors=plt.cm.Paired.colors)
    plt.title("Transaction Category Distribution")
    st.pyplot(plt)

    # Bar chart
    category_amounts = df.groupby("CATEGORY")[["WITHDRAWAL", "DEPOSIT"]].sum()
    category_amounts.plot(kind="bar", stacked=True, figsize=(10, 6), color=["orange", "green"])
    plt.title("Total Amount by Category")
    plt.xlabel("Category")
    plt.ylabel("Total Amount")
    plt.xticks(rotation=45)
    plt.legend(["Withdrawals", "Deposits"])
    st.pyplot(plt)

# Main function
def main():
    st.title("Bank Statement OCR & Categorization")

    uploaded_file = st.file_uploader("Upload Bank Statement Image", type=["png", "jpg", "jpeg"])
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        ocr_text = pytesseract.image_to_string(image)

        transactions = extract_transactions(ocr_text)
        df = pd.DataFrame(transactions, columns=["DATE", "DESCRIPTION", "WITHDRAWAL", "DEPOSIT", "BALANCE"])

        # Transform date format
        df["DATE"] = df["DATE"].apply(transform_date)

        # Remove rows where DATE is NULL
        df = df.dropna(subset=["DATE"])

        # Convert numeric columns
        df["WITHDRAWAL"] = pd.to_numeric(df["WITHDRAWAL"].replace(",", "", regex=True), errors='coerce')
        df["DEPOSIT"] = pd.to_numeric(df["DEPOSIT"].replace(",", "", regex=True), errors='coerce')
        df["BALANCE"] = pd.to_numeric(df["BALANCE"].replace(",", "", regex=True), errors='coerce')

        # Categorize transactions
        df = categorize_transactions(df)

        # Save to database
        save_to_database(df)

        # Display DataFrame
        st.subheader("Categorized Transactions")
        st.write(df)

        # Show charts
        show_charts(df)

if __name__ == "__main__":
    main()
