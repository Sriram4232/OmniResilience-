import asyncio
from agent import run_supply_chain_agent
import json

async def main():
    print("Testing Agent for Product P001...")
    result = await run_supply_chain_agent("P001")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
