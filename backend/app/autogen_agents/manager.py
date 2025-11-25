import os
from autogen import register_function
from app.rag.retriever import TaxRetriever
from .tax_expert import create_tax_expert
from .orchestrator import create_orchestrator

# Initialize Retriever
retriever = TaxRetriever()

def consult_tax_rules(query: str) -> str:
    """
    Searches the tax rules database for relevant information.
    Args:
        query: The search query string.
    Returns:
        A string containing the relevant tax rules.
    """
    print(f"[RAG] Searching for: {query}")
    docs = retriever.retrieve(query)
    if not docs:
        return "No relevant tax rules found."
    return "\n\n".join(docs)

async def run_autogen_chat(user_message: str):
    """
    Runs the AutoGen chat flow for a given user message.
    Returns the final response from the TaxExpert.
    """
    
    llm_config = {
        "config_list": [{
            "model": "gpt-4",
            "api_key": os.getenv("OPENAI_API_KEY")
        }],
        "temperature": 0
    }
    
    tax_expert = create_tax_expert(llm_config)
    orchestrator = create_orchestrator(llm_config)
    
    # Register the tool
    register_function(
        consult_tax_rules,
        caller=tax_expert,
        executor=orchestrator,
        name="consult_tax_rules",
        description="Search the tax rules database for relevant information."
    )
    
    # Initiate Chat
    # We want to capture the output. 
    # For simplicity, we'll let it run and return the last message from the expert.
    # But initiate_chat returns a ChatResult object in newer versions.
    
    chat_result = orchestrator.initiate_chat(
        tax_expert,
        message=user_message,
        summary_method="last_msg"
    )
    
    # Extract the final answer
    # The chat history is in chat_result.chat_history
    # We want the last message from TaxExpert that is not a tool call.
    
    # For now, just return the summary (last message)
    return chat_result.summary

