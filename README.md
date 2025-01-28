BFSI - OCR of Bank Statement 

Overview of this Project-

The BFSI (Banking, Financial Services, and Insurance) Data Analysis Platform is a Streamlit-based application that enables the processing and visualization of financial documents using Optical Character Recognition (OCR) and data clustering techniques.

Features:

Payslip Processing: Extracts and analyzes payslip data then give visualization.

Invoice Management: Processes invoices and extracts key financial details then give visualization.

Profit and Loss Analysis: Provides insights into profit and loss statements and give visualization.

Bank Statement Analysis: Categorises and visualizes bank transactions.

API Data Processing: Integrates and analyzes financial data from APIs and give visualization.

Unsupervised Data Clustering: Uses OCR & K-Means for document classification  and give visualization.


Installation:

Prerequisites

Ensure you have the following installed:

Python 3.x

Streamlit

MySQL

Required dependencies from requirements.txt

Project Structure:
├── supervised/
│   ├── payslip.py
│   ├── invoice.py
│   ├── profit_loss.py
│   ├── bank_statement.py
├── semi_supervised/
│   ├── api_data.py
├── unsupervised/
│   ├── bart_classification.py
├── app.py
├── requirements.txt
└── README.md


Usage:

To run the BFSI project:

Ensure the MySQL database is set up and the schema is created (refer to the Database section).

Activate your virtual environment (if not already active).

Run the Streamlit app:
streamlit run app.py




