import streamlit as st
from supervised.payslip import main as payslip_app
from supervised.invoice import main as invoice_app
from supervised.profit_loss import main as profit_loss_app
from supervised.bank_statement import main as bank_statement_app
from semi_supervised.api_data import main as api_data_app
from unsupervised.bart_classification import main as bart_classification_app 

def main():
    # Sidebar Title and Options
    st.sidebar.title("BFSI Project")
    options = [
        "Home",
        "Payslip",
        "Invoice",
        "Profit and Loss",
        "Bank Statement",
        "API Data",
        "Unsupervised Data Clustering (OCR & K-Means)"
    ]
    choice = st.sidebar.selectbox("Select Module", options)

    if choice == "Home":
        st.title("BFSI - Banking, Financial Services, and Insurance")
        st.write(
            """
            Welcome to the BFSI Data Analysis Platform. This tool allows you to process and visualize
            financial documents using Optical Character Recognition (OCR) and data clustering techniques.
            
            **Available Modules:**
            - Payslip Processing
            - Invoice Management
            - Profit and Loss Analysis
            - Bank Statement Analysis
            - API Data Processing
            - Unsupervised Data Clustering with OCR & K-Means
            
            Select a module from the sidebar to begin.
            """
        )
    else:
        # Show a loading spinner while switching modules
        with st.spinner(f"Loading {choice} module... Please wait"):
            if choice == "Payslip":
                st.title("Payslip Module")
                payslip_app()

            elif choice == "Invoice":
                st.title("Invoice Module")
                invoice_app()

            elif choice == "Profit and Loss":
                st.title("Profit and Loss Module")
                profit_loss_app()

            elif choice == "Bank Statement":
                st.title("Bank Statement Module")
                bank_statement_app()

            elif choice == "API Data":
                st.title("API Data Module")
                api_data_app()

            elif choice == "Unsupervised Data Clustering (OCR & K-Means)":
                st.title("Unsupervised Data Clustering")
                bart_classification_app()

if __name__ == "__main__":
    main()
