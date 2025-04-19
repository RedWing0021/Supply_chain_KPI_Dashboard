# compute_kpis.py

import pandas as pd
from sqlalchemy import create_engine

# MySQL connection
MYSQL_USER = 'root'
MYSQL_PASSWORD = 'admin123'
MYSQL_HOST = 'localhost'
MYSQL_PORT = '3306'
MYSQL_DB = 'supply_chain'

engine = create_engine(f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}")

# 1. Load the cleaned CSV to MySQL
df = pd.read_csv("dataset/cleaned_orders.csv")

# Clean column names
df.columns = df.columns.str.strip()

# Export the cleaned data to the 'orders' table in MySQL
try:
    df.to_sql('orders', con=engine, index=False, if_exists='replace')
    print("✅ Data successfully loaded into MySQL 'orders' table.")
except Exception as e:
    print("❌ Failed to load data:", e)

# 2. SQL Queries to compute KPIs

query_inventory_turnover = """
    SELECT `Category Name` AS ProductCategory,
           ROUND(SUM(Sales) / NULLIF(AVG(OrderQuantity), 0), 2) AS InventoryTurnover
    FROM orders
    GROUP BY `Category Name`;
"""

query_lead_time = """
    SELECT `Category Name` AS ProductCategory,
           ROUND(AVG(DATEDIFF(`ShippingDate`, `OrderDate`)), 2) AS AvgLeadTime
    FROM orders
    WHERE `ShippingDate` IS NOT NULL AND `OrderDate` IS NOT NULL
    GROUP BY `Category Name`;
"""

query_fill_rate = """
    SELECT 
        ROUND(100 - (COUNT(CASE WHEN DeliveryStatus = 'Late delivery' THEN 1 END) * 100.0 / COUNT(*)), 2) AS FillRate
    FROM orders;
"""

# 3. Run queries to compute KPIs
try:
    inv_df = pd.read_sql(query_inventory_turnover, engine)
    lead_df = pd.read_sql(query_lead_time, engine)
    fill_df = pd.read_sql(query_fill_rate, engine)
    print("✅ KPI queries executed successfully.")
except Exception as e:
    print("❌ Failed to run KPI queries:", e)

# 4. Merge data to combine KPIs
try:
    kpi_df = inv_df.merge(lead_df, on='ProductCategory', how='outer')
    kpi_df['FillRate'] = fill_df.iloc[0]['FillRate']  # Assuming a single fill rate for all categories
except Exception as e:
    print("❌ Failed to merge KPI data:", e)

# 5. Save KPIs to CSV for Power BI/Tableau
output_path = "output/kpis_final.csv"
try:
    kpi_df.to_csv(output_path, index=False)
    print(f"✅ KPIs exported to '{output_path}'.")
except Exception as e:
    print("❌ Failed to export KPIs to CSV:", e)
