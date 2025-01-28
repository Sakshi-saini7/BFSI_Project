import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
import os
import pymysql
from io import StringIO  # Import StringIO for wrapping HTML content

# MySQL Connection Setup using PyMySQL
def connect_db():
    return pymysql.connect(
        host="localhost",      # Your MySQL host
        user="root",           # Your MySQL username
        password="sql777save##",   # Your MySQL password
        database="semi_supervised_"  # Your database name
    )

# Ensure the 'financial_data' directory exists
if not os.path.exists("financial_data"):
    os.makedirs("financial_data")

# Financial Data Scraping Function
def scrape_financial_data(ticker):
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0'
    }

    urls = {
        'ratio annually': f"https://stockanalysis.com/stocks/{ticker}/financials/ratios/"
    }

    for key in urls.keys():
        response = requests.get(urls[key], headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        # Wrap HTML content in StringIO to remove deprecation warning
        html_content = StringIO(str(soup))
        df = pd.read_html(html_content, attrs={'data-test': 'financials'})[0]
        
        # Save to a CSV file
        file_name = f'financial_statements_{key}.csv'
        file_path = os.path.join("financial_data", file_name)
        df.to_csv(file_path, index=False, encoding='utf-8')
        
        st.write(f"Financial data saved: {file_name}")
        st.download_button(label="Download CSV", data=open(file_path, 'r').read(), file_name=file_name, mime="text/csv")

        # Insert CSV data into MySQL
        insert_csv_to_db(file_path)

# Insert CSV Data into MySQL
import numpy as np

def insert_csv_to_db(file_path):
    # Load the CSV data into a DataFrame
    data = pd.read_csv(file_path)

    # Standardize column names to match MySQL table
    column_mapping = {
        "Fiscal Year": "Fiscal_Year",
        "Current": "Current",
        "FY 2024": "FY_2024",
        "FY 2023": "FY_2023",
        "FY 2022": "FY_2022",
        "FY 2021": "FY_2021",
        "FY 2020": "FY_2020",
        "2019 - 2015": "2019-2015"
    }
    data.rename(columns=column_mapping, inplace=True)

    # Remove unwanted characters (%, ,) and convert numeric columns to string
    numeric_columns = ["Current", "FY_2024", "FY_2023", "FY_2022", "FY_2021", "FY_2020", "2019-2015"]

    for col in numeric_columns:
        data[col] = data[col].astype(str).str.replace(',', '').str.replace('%', '').str.strip()

    # Replace NaN with an empty string ("") or NULL as per preference
    data = data.applymap(lambda x: None if isinstance(x, str) and x == "nan" else x)  # Convert string "nan" to None

    # Connect to MySQL database
    conn = connect_db()
    cursor = conn.cursor()

    # Insert data row by row
    for _, row in data.iterrows():
        cursor.execute("""
            INSERT INTO financial_statement_ratio_annually_ (Fiscal_Year, Current, FY_2024, FY_2023, FY_2022, FY_2021, FY_2020, `2019-2015`)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            row["Fiscal_Year"], 
            row["Current"] if pd.notna(row["Current"]) else None, 
            row["FY_2024"] if pd.notna(row["FY_2024"]) else None, 
            row["FY_2023"] if pd.notna(row["FY_2023"]) else None, 
            row["FY_2022"] if pd.notna(row["FY_2022"]) else None, 
            row["FY_2021"] if pd.notna(row["FY_2021"]) else None, 
            row["FY_2020"] if pd.notna(row["FY_2020"]) else None, 
            row["2019-2015"] if pd.notna(row["2019-2015"]) else None
        ))

    # Commit and close the connection
    conn.commit()
    cursor.close()
    conn.close()

    st.write("CSV data inserted into the database.")


# Visualization Function
def visualize_financial_data(file_path):
    # Load the CSV file
    data = pd.read_csv(file_path)

    # Clean data
    data.columns = ['Fiscal Year', 'Current', 'FY_2024', 'FY_2023', 'FY_2022', 'FY_2021', 'FY_2020', '2019-2015']
    data.set_index('Fiscal Year', inplace=True)

    # Clean Numeric Data
    cleaned_data = data.copy()
    for col in cleaned_data.columns:
        cleaned_data[col] = cleaned_data[col].replace({',': '', '%': ''}, regex=True).apply(pd.to_numeric, errors='coerce')

    # Market Cap Trends (Bar Chart)
    st.subheader("Market Capitalization Trends")
    plt.figure(figsize=(10, 6))
    cleaned_data.loc['Market Capitalization'].plot(kind='bar', color='skyblue', edgecolor='black')
    plt.title('Market Capitalization Trends Over Fiscal Years', fontsize=16)
    plt.xlabel('Fiscal Year', fontsize=12)
    plt.ylabel('Market Cap (in Millions)', fontsize=12)
    plt.xticks(rotation=45)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    st.pyplot(plt)

    # Market Cap Growth (Line Chart)
    st.subheader("Market Cap Growth (YoY)")
    plt.figure(figsize=(10, 6))
    cleaned_data.loc['Market Cap Growth'].plot(kind='line', marker='o', color='orange', linewidth=2)
    plt.title('Market Cap Growth (YoY)', fontsize=16)
    plt.xlabel('Fiscal Year', fontsize=12)
    plt.ylabel('Growth Rate (%)', fontsize=12)
    plt.xticks(rotation=45)
    plt.grid(axis='both', linestyle='--', alpha=0.7)
    st.pyplot(plt)

# Streamlit Interface
def main():
    st.title("Financial Data Scraping and Visualization")

    # User input for ticker symbol
    ticker = st.text_input("Enter Ticker Symbol", value="AAPL")

    # Scrape financial data
    if st.button("Scrape Financial Data"):
        scrape_financial_data(ticker)
    
    # Load and visualize data
    uploaded_file = st.file_uploader("Upload CSV File", type=["csv"])
    if uploaded_file is not None:
        visualize_financial_data(uploaded_file)

if __name__ == "__main__":
    main()
