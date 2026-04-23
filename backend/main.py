import os
import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

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

def get_inventory_data():
    with open('../data/mock_data/sales.json', 'r') as f:
        return json.load(f)

def get_disruptions_data():
    with open('../data/mock_data/disruptions.json', 'r') as f:
        return json.load(f)

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

