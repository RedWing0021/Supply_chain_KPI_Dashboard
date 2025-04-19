# ingest_data.py

import pandas as pd
from sqlalchemy import create_engine

# MySQL connection parameters
MYSQL_USER = 'root'
MYSQL_PASSWORD = 'admin123'
MYSQL_HOST = 'localhost'
MYSQL_PORT = '3306'
MYSQL_DB = 'supply_chain'

# Path to the dataset
DATA_PATH = "data/DataCoSupplyChainDataset.csv"

# Establish connection
engine = create_engine(f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}")

# Load the dataset
df = pd.read_csv(DATA_PATH, encoding='ISO-8859-1')

df.columns = df.columns.str.strip()

# Rename columns to cleaner, SQL-friendly names
df.rename(columns={
    'order date (DateOrders)': 'OrderDate',
    'shipping date (DateOrders)': 'ShippingDate',
    'Delivery Status': 'DeliveryStatus',
    'Product Category': 'ProductCategory',  # Note: this might not exist; use 'Category Name' if needed
    'Order Item Quantity': 'OrderQuantity',
    'Product Card Id': 'ProductCardId',
    'Customer Segment': 'CustomerSegment',
    'Sales': 'Sales'
}, inplace=True)

# Convert dates
df['OrderDate'] = pd.to_datetime(df['OrderDate'], errors='coerce')
df['ShippingDate'] = pd.to_datetime(df['ShippingDate'], errors='coerce')


# Export cleaned data to CSV
output_path = "dataset/cleaned_orders.csv"
try:
    df.to_csv(output_path, index=False)
    print(f"✅ Cleaned data exported to '{output_path}'.")
except Exception as e:
    print("❌ Failed to export cleaned CSV:", e)