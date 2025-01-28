import streamlit as st
import pytesseract
from PIL import Image
import pandas as pd
import re
import matplotlib.pyplot as plt
import pymysql

# Set up Tesseract executable path (adjust for your system)
pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

# MySQL connection function
def create_connection():
    connection = pymysql.connect(
        host="localhost",  # MySQL host
        user="root",       # MySQL username
        password="sql777save##",  # MySQL password
        database="supervised"  # Your database name
    )
    return connection

# Function to insert profit and loss data into the MySQL database
def insert_profit_loss_to_db(dataframe):
    connection = create_connection()
    cursor = connection.cursor()

    # Insert each row into the MySQL database
    for index, row in dataframe.iterrows():
        cursor.execute("""
            INSERT INTO profit_loss (category, amount)
            VALUES (%s, %s)
        """, (row['Category'], row['Amount']))

    connection.commit()
    cursor.close()
    connection.close()

# Function to extract text from image
def extract_text(image):
    return pytesseract.image_to_string(image)

# Function to extract profit and loss data
def extract_profit_loss_data(text):
    data = []
    lines = text.split("\n")
    for line in lines:
        match = re.match(r"(.*?)([£\$]?\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?)$", line)
        if match:
            category = match.group(1).strip()
            amount = match.group(2).replace(",", "").replace("£", "").replace("$", "").strip()
            data.append((category, float(amount)))
    return data

# Function to visualize bar chart
def visualize_bar_chart(data):
    st.subheader("Bar Chart")
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(data["Category"], data["Amount"], color="skyblue")
    ax.set_xlabel("Category", fontsize=12)
    ax.set_ylabel("Amount", fontsize=12)
    ax.set_title("Profit and Loss Breakdown (Bar Chart)", fontsize=14)
    plt.xticks(rotation=45, ha="right")
    st.pyplot(fig)

# Function to visualize pie chart
def visualize_pie_chart(data):
    st.subheader("Pie Chart")
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.pie(data["Amount"], labels=data["Category"], autopct="%1.1f%%", startangle=140, colors=plt.cm.tab20.colors)
    ax.set_title("Profit and Loss Breakdown (Pie Chart)", fontsize=14)
    st.pyplot(fig)

# Main function
def main():
    st.title("Profit and Loss Analysis")
    st.write("Upload an image of your Profit and Loss document to extract and analyze data.")

    uploaded_file = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"])
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_container_width=True)

        # Extract text using OCR
        with st.spinner("Extracting text from the image..."):
            extracted_text = extract_text(image)
        st.text_area("Extracted Text", extracted_text, height=200)

        # Extract and process profit and loss data
        profit_loss_data = extract_profit_loss_data(extracted_text)
        if profit_loss_data:
            df = pd.DataFrame(profit_loss_data, columns=["Category", "Amount"])
            st.dataframe(df)

            # Insert the data into the MySQL database
            insert_profit_loss_to_db(df)

            # Save extracted data to CSV
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("Download Data as CSV", data=csv, file_name="profit_and_loss_data.csv", mime="text/csv")

            # Visualize data
            visualize_bar_chart(df)
            visualize_pie_chart(df)
        else:
            st.warning("No valid profit and loss data found in the uploaded image.")

if __name__ == "__main__":
    main()
