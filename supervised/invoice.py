import streamlit as st
import pytesseract
from PIL import Image
import pandas as pd
import re
import matplotlib.pyplot as plt
import pymysql

# Set up Tesseract executable path (adjust the path as per your system configuration)
pytesseract.pytesseract.tesseract_cmd = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"

# MySQL connection function
def create_connection():
    connection = pymysql.connect(
        host="localhost",  # MySQL host
        user="root",       # MySQL username
        password="sql777save##",  # MySQL password
        database="supervised"  # Your database name
    )
    return connection

# Function to insert invoice data into the MySQL database
def insert_invoice_to_db(dataframe):
    connection = create_connection()
    cursor = connection.cursor()

    # Insert each row into the MySQL database
    for index, row in dataframe.iterrows():
        cursor.execute("""
            INSERT INTO invoice (item, quantity, unit_price, total)
            VALUES (%s, %s, %s, %s)
        """, (row['Item'], row['Quantity'], row['Unit Price'], row['Total']))

    connection.commit()
    cursor.close()
    connection.close()

# Function to extract expenses from the invoice text
def extract_invoice_expenses(text):
    expenses = []
    lines = text.split("\n")
    for line in lines:
        # Match item description, quantity, unit price, and total price
        match = re.match(r"(.*?)(\d+)\s+\$([\d,]+)\s+\$([\d,]+)$", line)
        if match:
            item = match.group(1).strip()
            quantity = int(match.group(2))
            unit_price = float(match.group(3).replace(",", ""))
            total = float(match.group(4).replace(",", ""))
            expenses.append((item, quantity, unit_price, total))
    return expenses

# Function to visualize data as a bar chart
def visualize_bar_chart(data):
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(data["Item"], data["Total"], color="skyblue")
    ax.set_xlabel("Item", fontsize=12)
    ax.set_ylabel("Total ($)", fontsize=12)
    ax.set_title("Invoice Expenses Breakdown (Bar Chart)", fontsize=14)
    ax.tick_params(axis="x", rotation=45)
    st.pyplot(fig)

# Function to visualize data as a pie chart
def visualize_pie_chart(data):
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.pie(
        data["Total"], 
        labels=data["Item"], 
        autopct="%1.1f%%", 
        startangle=140, 
        colors=plt.cm.tab20.colors
    )
    ax.set_title("Invoice Expenses Breakdown (Pie Chart)", fontsize=14)
    st.pyplot(fig)

# Main function for Streamlit app
def main():
    st.title("Invoice OCR and Visualization")
    st.write("Upload an invoice image to extract and visualize expenses.")

    uploaded_file = st.file_uploader("Upload Invoice Image", type=["png", "jpg", "jpeg"])

    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Invoice", use_container_width=True)

        # Perform OCR on the uploaded image
        with st.spinner("Extracting text from the invoice..."):
            ocr_text = pytesseract.image_to_string(image)
        
        # Extract expenses
        invoice_expenses = extract_invoice_expenses(ocr_text)

        if invoice_expenses:
            # Convert to DataFrame
            df = pd.DataFrame(invoice_expenses, columns=["Item", "Quantity", "Unit Price", "Total"])
            st.success("Expenses extracted successfully!")
            st.write("Extracted Data:")
            st.dataframe(df)

            # Insert the data into the MySQL database
            insert_invoice_to_db(df)

            # Visualization options
            st.write("### Visualizations:")
            col1, col2 = st.columns(2)

            with col1:
                st.write("**Bar Chart**")
                visualize_bar_chart(df)
            
            with col2:
                st.write("**Pie Chart**")
                visualize_pie_chart(df)
        else:
            st.error("No valid expenses found in the invoice.")

if __name__ == "__main__":
    main()
