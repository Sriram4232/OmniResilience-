import os
import json
import psycopg2
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

def init_postgres():
    print("Connecting to PostgreSQL...")
    conn = psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", "5432"),
        dbname=os.getenv("POSTGRES_DB", "omniresilience"),
        user=os.getenv("POSTGRES_USER", "user"),
        password=os.getenv("POSTGRES_PASSWORD", "password")
    )
    cur = conn.cursor()
    
    # Create tables
    cur.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            product_id VARCHAR(50) PRIMARY KEY,
            name VARCHAR(255),
            category VARCHAR(100),
            current_stock INT,
            reorder_point INT,
            demand_forecast VARCHAR(50),
            supplier VARCHAR(255)
        )
    """)
    
    # Check if empty
    cur.execute("SELECT COUNT(*) FROM inventory")
    if cur.fetchone()[0] == 0:
        print("Populating PostgreSQL with mock sales data...")
        with open('../mock_data/sales.json', 'r') as f:
            sales_data = json.load(f)
            for item in sales_data:
                cur.execute("""
                    INSERT INTO inventory 
                    (product_id, name, category, current_stock, reorder_point, demand_forecast, supplier)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    item['product_id'], item['name'], item['category'], 
                    item['current_stock'], item['reorder_point'], 
                    item['demand_forecast'], item['supplier']
                ))
    else:
        print("PostgreSQL already populated.")
        
    conn.commit()
    cur.close()
    conn.close()

def init_mongodb():
    print("Connecting to MongoDB...")
    mongo_uri = os.getenv("MONGO_URI", "mongodb://root:example@localhost:27017/")
    client = MongoClient(mongo_uri)
    db = client[os.getenv("MONGO_DB", "omniresilience")]
    collection = db['disruptions']
    
    if collection.count_documents({}) == 0:
        print("Populating MongoDB with mock disruptions...")
        with open('../mock_data/disruptions.json', 'r') as f:
            disruptions_data = json.load(f)
            collection.insert_many(disruptions_data)
    else:
        print("MongoDB already populated.")

if __name__ == "__main__":
    init_postgres()
    init_mongodb()
    print("Initialization complete.")
