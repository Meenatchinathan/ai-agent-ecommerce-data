import pandas as pd
import sqlite3
from sqlalchemy import create_engine
import os

# Google Sheets URLs
DATASETS = {
    "eligibility_table": "https://docs.google.com/spreadsheets/d/1Loc32KsHwEGhLAahSfMA6t1aZdEvxJIPADxpdzZEZTw/export?format=csv&gid=95626969",
    "ad_sales_metrics": "https://docs.google.com/spreadsheets/d/1ZATJteA4sU7DXN-fqJxG8Td_Nwif5QB2fTQvGK8LegY/export?format=csv",
    "total_sales_metrics": "https://docs.google.com/spreadsheets/d/1ftXt9Z6uEXUMlIHSZK0CR2kLlNZyj8TUi4lQmMF6qWo/export?format=csv"
}

def clean_column_name(name):
    """Clean column names for SQL compatibility"""
    return name.replace(' ', '_').replace('(', '').replace(')', '').replace('/', '_').replace('%', 'pct')

def load_data_to_sqlite(db_path="database/ecommerce.db"):
    # Create database directory if not exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    engine = create_engine(f"sqlite:///{db_path}")
    
    for table_name, url in DATASETS.items():
        print(f"Loading {table_name} from {url}")
        df = pd.read_csv(url)
        
        # Clean column names
        df.columns = [clean_column_name(col) for col in df.columns]
        
        # Save to SQLite
        df.to_sql(table_name, engine, if_exists="replace", index=False)
        print(f"Loaded {len(df)} rows to {table_name}")
    
    print(f"Database created at {db_path}")

if __name__ == "__main__":
    load_data_to_sqlite()