import pytesseract
from PIL import Image
import csv
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import pymysql

# Ensure Tesseract is installed and its path is set
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

# Function to insert data into the MySQL database
def insert_data_to_db(dataframe):
    connection = create_connection()
    cursor = connection.cursor()

    # Insert each row into the MySQL database
    for index, row in dataframe.iterrows():
        cursor.execute("""
            INSERT INTO payslip (expense, amount)
            VALUES (%s, %s)
        """, (row['Expense'], row['Amount']))

    connection.commit()
    cursor.close()
    connection.close()

# Function to extract text from the image
def extract_text(image_path):
    img = Image.open(image_path)
    text = pytesseract.image_to_string(img)
    return text

# Function to parse the Earnings section
def parse_earnings_section(text):
    lines = text.split("\n")
    earnings_section = []
    capture = False

    for line in lines:
        if "Earnings" in line:  # Start capturing after this line
            capture = True
        elif "Net Salary" in line:  # Stop capturing when this line is reached
            capture = False
        elif capture and line.strip():  # Add valid lines to the list
            earnings_section.append(line.strip())
    
    # Parse the extracted earnings into field-value pairs
    parsed_earnings = []
    for entry in earnings_section:
        if any(char.isdigit() for char in entry):  # Check for numeric values
            parts = entry.rsplit(" ", 1)  # Split at the last space for field and value
            if len(parts) == 2:
                field, value = parts
                parsed_earnings.append([field.strip(), value.strip()])
    
    return parsed_earnings

# Function to save the parsed data to CSV
def save_to_csv(data, csv_filename):
    with open(csv_filename, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Expense", "Amount"])  # Header
        writer.writerows(data)

# Function to visualize bar chart in Streamlit
def visualize_bar_chart(data):
    st.subheader("Bar Chart: Expense Breakdown")
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(data["Expense"], data["Amount"], color="skyblue")
    ax.set_xlabel("Expense Category", fontsize=12)
    ax.set_ylabel("Amount", fontsize=12)
    ax.set_title("Expenses Breakdown (Bar Chart)", fontsize=14)
    plt.xticks(rotation=45, ha="right")
    st.pyplot(fig)

# Function to visualize pie chart in Streamlit
def visualize_pie_chart(data):
    st.subheader("Pie Chart: Expense Breakdown")
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.pie(
        data["Amount"],
        labels=data["Expense"],
        autopct="%1.1f%%",
        startangle=140,
        colors=plt.cm.tab20.colors,
    )
    ax.set_title("Expenses Breakdown (Pie Chart)", fontsize=14)
    st.pyplot(fig)

# Main function for Streamlit
def main():
    st.title("Payslip OCR and Visualization")

    # File uploader for payslip image
    uploaded_file = st.file_uploader("Upload your payslip image", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        # Extract text from the uploaded payslip
        extracted_text = extract_text(uploaded_file)
        st.text_area("Extracted Text", value=extracted_text, height=200)

        # Parse the Earnings section
        earnings_data = parse_earnings_section(extracted_text)
        if earnings_data:
            st.success("Earnings section extracted successfully!")
            st.write("Parsed Earnings Data:", earnings_data)

            # Save to a temporary CSV file
            csv_path = "temp_payslip.csv"
            save_to_csv(earnings_data, csv_path)

            # Load the CSV data into a DataFrame
            data = pd.DataFrame(earnings_data, columns=["Expense", "Amount"])
            data["Amount"] = pd.to_numeric(data["Amount"], errors="coerce")

            # Show the DataFrame in Streamlit
            st.subheader("Parsed Payslip Data")
            st.dataframe(data)

            # Insert the data into the MySQL database
            insert_data_to_db(data)

            # Visualizations
            visualize_bar_chart(data)
            visualize_pie_chart(data)
        else:
            st.warning("Could not extract earnings data. Please check the uploaded image.")

if __name__ == "__main__":
    main()
