import os
import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import psycopg2
from pymongo import MongoClient

# We will import the agent logic
from agent import run_supply_chain_agent

load_dotenv()

app = FastAPI(title="OmniResilience AI API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# PostgreSQL (Supabase) connection
def get_postgres_connection():
    conn = psycopg2.connect(
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT", "5432"),
        database=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        sslmode="require"
    )
    return conn

# MongoDB Atlas connection
def get_mongo_client():
    mongo_uri = os.getenv("MONGO_URI")
    client = MongoClient(mongo_uri)
    return client

def get_inventory_data():
    try:
        conn = get_postgres_connection()
        cur = conn.cursor()
        cur.execute("SELECT product_id, name, category, current_stock, reorder_point, demand_forecast, supplier FROM inventory")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        
        inventory = []
        for row in rows:
            inventory.append({
                "product_id": row[0],
                "name": row[1],
                "category": row[2],
                "current_stock": row[3],
                "reorder_point": row[4],
                "demand_forecast": row[5],
                "supplier": row[6]
            })
        return inventory
    except Exception as e:
        print(f"Error fetching inventory: {e}")
        return []

def get_disruptions_data():
    try:
        client = get_mongo_client()
        db = client[os.getenv("MONGO_DB", "omniresilience")]
        collection = db['disruptions']
        disruptions = list(collection.find({}, {"_id": 0}))
        client.close()
        return disruptions
    except Exception as e:
        print(f"Error fetching disruptions: {e}")
        return []

@app.get("/")
def read_root():
    return {"message": "Welcome to OmniResilience AI API"}

@app.get("/api/inventory")
def get_inventory():
    return {"inventory": get_inventory_data()}

@app.get("/api/disruptions")
def get_disruptions():
    return {"disruptions": get_disruptions_data()}

class AgentRequest(BaseModel):
    product_id: str

@app.post("/api/analyze")
async def analyze_product(req: AgentRequest):
    # Run the langgraph agent for this product
    result = await run_supply_chain_agent(req.product_id)
    return result
