import asyncio
import os
from dotenv import load_dotenv

# Load env vars
if not load_dotenv():
    load_dotenv(os.path.join(os.path.dirname(__file__), '../.env'))

from app.autogen_agents.manager import run_autogen_chat

async def main():
    print("Testing AutoGen Tax Expert...")
    question = "What is the tax slab for 8 lakhs income in the new regime?"
    print(f"Question: {question}")
    
    response = await run_autogen_chat(question)
    
    print("\nFinal Response:")
    print(response)

if __name__ == "__main__":
    asyncio.run(main())
