import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import streamlit as st
import pymysql

# Function to create a database connection
def create_connection(): 
    connection = pymysql.connect(
        host="localhost",       # Replace with your host
        user="root",            # Replace with your MySQL username
        password="sql777save##",# Replace with your MySQL password
        database="unsupervised" # Replace with your database name
    )
    return connection

# Function to save data into the MySQL database
def save_to_database(df, table_name="supervised.bank_statement"):
    try:
        connection = create_connection()
        cursor = connection.cursor()

        # Insert data row by row
        for index, row in df.iterrows():
            cursor.execute(f"""
                INSERT INTO {table_name} (date, description, withdrawal, deposit, balance, category)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                row['Date'], 
                row['Description'], 
                row['Transaction_Amount'] if row['Transaction_Amount'] < 0 else None,  # Withdrawal if amount is negative
                row['Transaction_Amount'] if row['Transaction_Amount'] >= 0 else None,  # Deposit if amount is positive
                row['Balance'], 
                row['Category'] if 'Category' in row else 'Uncategorized'  # Default to 'Uncategorized' if no category
            ))

        connection.commit()
        st.success(f"Data saved to the '{table_name}' table successfully!")
    except Exception as e:
        st.error(f"Error saving data to the database: {e}")
    finally:
        if connection:
            connection.close()

# Perform K-Means Clustering
def perform_kmeans(df, num_clusters=3):
    # Select numerical columns for clustering
    clustering_features = ['Transaction_Amount', 'Balance']
    data = df[clustering_features]

    # Standardize the data
    scaler = StandardScaler()
    data_scaled = scaler.fit_transform(data)

    # Apply K-Means Clustering
    kmeans = KMeans(n_clusters=num_clusters, random_state=42)
    df['Cluster'] = kmeans.fit_predict(data_scaled)

    return df, kmeans

# Visualization
def visualize_clusters(df, num_clusters):
    st.subheader("Cluster Distribution - Pie Chart")
    cluster_counts = df['Cluster'].value_counts()
    plt.figure(figsize=(6, 6))
    plt.pie(
        cluster_counts, 
        labels=[f'Cluster {i}' for i in range(num_clusters)], 
        autopct='%1.1f%%', 
        startangle=90, 
        colors=plt.cm.Paired.colors
    )
    plt.title("Cluster Distribution")
    st.pyplot(plt)

    st.subheader("Cluster-wise Total Transaction Amount - Bar Chart")
    cluster_sums = df.groupby('Cluster')['Transaction_Amount'].sum()
    plt.figure(figsize=(8, 5))
    cluster_sums.plot(kind='bar', color=plt.cm.Paired.colors)
    plt.title("Total Transaction Amount by Cluster")
    plt.xlabel("Cluster")
    plt.ylabel("Total Transaction Amount")
    plt.xticks(rotation=0)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    st.pyplot(plt)

# Streamlit App
def main():
    st.title("Unsupervised Data - K-Means Clustering on Bank Statement")

    # File uploader for CSV
    uploaded_file = st.file_uploader("Upload your bank statement CSV file", type=["csv"])

    if uploaded_file is not None:
        # Load data from the uploaded file
        df = pd.read_csv(uploaded_file)

        st.write("### Input Data:")
        st.dataframe(df)  # Display the uploaded dataframe

        # Automatically save data to the database upon upload
        save_to_database(df)

        # Perform clustering
        if st.button("Perform Clustering"):
            st.write("### Processing Clustering...")
            clustered_df, kmeans = perform_kmeans(df)

            st.write("### Output Data:")
            st.dataframe(clustered_df)  # Display the clustered dataframe

            # Visualize clusters
            visualize_clusters(clustered_df, num_clusters=3)

if __name__ == "__main__":
    main()
