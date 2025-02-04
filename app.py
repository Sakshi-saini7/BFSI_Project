import streamlit as st
from supervised.payslip import main as payslip_app
from supervised.invoice import main as invoice_app
from supervised.profit_loss import main as profit_loss_app
from supervised.bank_statement import main as bank_statement_app
from semi_supervised.api_data import main as api_data_app
from unsupervised.bart_classification import main as bart_classification_app

# Set Page Configuration
st.set_page_config(page_title="FinVision: Financial Data Visualization", page_icon="\U0001F4B0", layout="wide")

def main():
    # Sidebar with Branding
    st.sidebar.title("FinVision: BFSI Data Visualization Platform")
    st.sidebar.markdown("**Streamlining Financial Data Processing & Visualization**")
    
    # Home Dashboard (initial page)
    st.title("BFSI - Banking, Financial Services, and Insurance \U0001F4B8")
    st.markdown(
        """
        Welcome to the **BFSI Data Analysis Platform**, your one-stop solution for processing and visualizing
        financial documents using **Optical Character Recognition (OCR)** and **Data Clustering Techniques**.
        
        📌 Features:

        📑 Payslip Processing - Extract and analyze payslip details.
        
        🧾 Invoice Management- Automate invoice data extraction and give visulization.
        
        📊 Profit and Loss Analysis- Gain financial insights.
        
        🏦 Bank Statement Analysis- Understand transaction trends.
        
        🔗 API Data Processing- Integrate with external data sources.
        
        🤖 Unsupervised Data Clustering- Classify financial data using Clustering.
        
        👈🏻 Use the sidebar to navigate between modules.
        """
    )
    
    # Main Category Selection
    category = st.sidebar.radio("Select Category", ["Home", "Supervised", "Semi-supervised", "Unsupervised"], index=0)
    
    if category == "Supervised":
        sub_choice = st.sidebar.radio("Choose a Module", ["Payslip", "Invoice", "Profit and Loss", "Bank Statement"])
    elif category == "Semi-supervised":
        sub_choice = "API Data"
    elif category == "Unsupervised":
        sub_choice = "Unsupervised Data Clustering"
    else:
        sub_choice = None
    
    # Loading the selected module
    if sub_choice:
        with st.spinner(f"Loading {sub_choice} module... Please wait"):
            if sub_choice == "Payslip":
                payslip_app()
            elif sub_choice == "Invoice":
                invoice_app()
            elif sub_choice == "Profit and Loss":
                profit_loss_app()
            elif sub_choice == "Bank Statement":
                bank_statement_app()
            elif sub_choice == "API Data":
                api_data_app()
            elif sub_choice == "Unsupervised Data Clustering":
                bart_classification_app()

if __name__ == "__main__":
    main()
