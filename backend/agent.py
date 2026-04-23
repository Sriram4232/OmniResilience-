import os
import json
from typing import TypedDict, Annotated, List, Dict, Any
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

load_dotenv()

llm = None

groq_key = os.getenv("GROQ_API_KEY")

if groq_key:
    from langchain_groq import ChatGroq
    llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0, api_key=groq_key)

class AgentState(TypedDict):
    product_id: str
    inventory_data: Dict[str, Any]
    disruptions_data: List[Dict[str, Any]]
    analysis: str
    strategy: Dict[str, Any]

def get_inventory():
    with open('../data/mock_data/sales.json', 'r') as f:
        return json.load(f)

def get_disruptions():
    with open('../data/mock_data/disruptions.json', 'r') as f:
        return json.load(f)

async def fetch_data_node(state: AgentState):
    product_id = state['product_id']
    inv = get_inventory()
    dis = get_disruptions()
    
    product_inv = next((item for item in inv if item["product_id"] == product_id), None)
    
    # Simple logic: get all active disruptions that might affect this category or supplier
    relevant_dis = []
    if product_inv:
        for d in dis:
            if d.get("status") == "Active" and (product_inv["supplier"] in d["content"] or product_inv["category"] in d["content"] or "shipping" in d["content"].lower()):
                relevant_dis.append(d)
                
    return {"inventory_data": product_inv, "disruptions_data": relevant_dis}

async def analyze_node(state: AgentState):
    if not llm:
        return {"analysis": "Error: No LLM configured. Please provide GROQ_API_KEY in .env."}
        
    inv = state.get("inventory_data")
    dis = state.get("disruptions_data")
    
    if not inv:
        return {"analysis": "Product not found."}
        
    prompt = f"""
    You are an AI Merchandising and Supply Chain Agent.
    Analyze the following inventory and disruption data for a product and determine the impact.
    
    Inventory: {json.dumps(inv)}
    Disruptions: {json.dumps(dis)}
    
    Provide a concise risk analysis. Look for stockouts, overstock risks, supply chain delays, and demand mismatches.
    """
    
    response = llm.invoke([HumanMessage(content=prompt)])
    return {"analysis": response.content}

async def generate_strategy_node(state: AgentState):
    if not llm:
        return {"strategy": {"error": "No LLM configured"}}

    inv = state.get("inventory_data")
    analysis = state.get("analysis")
    
    if not inv:
        return {"strategy": {"error": "Product not found"}}
        
    prompt = f"""
    Based on the following inventory data and risk analysis, generate an actionable strategy for the product.
    Inventory: {json.dumps(inv)}
    Risk Analysis: {analysis}
    
    Return your strategy EXACTLY as a JSON object with the following keys, and nothing else (no markdown formatting, no code blocks):
    {{
        "recommended_action": "e.g. Expedite Shipping, Apply Markdown, Hold Price",
        "markdown_timing": "e.g. Immediate 15% discount, Wait 2 weeks, None",
        "replenishment_order_adjustment": "e.g. Increase by 50 units, Cancel pending orders",
        "expected_margin_impact": "e.g. Protected, -5%, +2%"
    }}
    """
    
    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        content = response.content.replace('```json', '').replace('```', '').strip()
        strategy_json = json.loads(content)
        return {"strategy": strategy_json}
    except Exception as e:
        return {"strategy": {"error": f"Failed to parse LLM output. Raw: {response.content}"}}

async def run_supply_chain_agent(product_id: str):
    # Initialize state
    state: AgentState = {
        "product_id": product_id,
        "inventory_data": {},
        "disruptions_data": [],
        "analysis": "",
        "strategy": {}
    }
    
    # 1. Fetch Data
    fetch_result = await fetch_data_node(state)
    state.update(fetch_result)
    
    # 2. Analyze
    analyze_result = await analyze_node(state)
    state.update(analyze_result)
    
    # 3. Generate Strategy
    strategy_result = await generate_strategy_node(state)
    state.update(strategy_result)
    
    return {
        "product_id": state["product_id"],
        "analysis": state["analysis"],
        "strategy": state["strategy"]
    }
