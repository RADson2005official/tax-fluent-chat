"""AutoGen Manager - Optional Wrapper.

This module wraps AutoGen functionality with graceful fallback
when pyautogen is not compatible with the current Python version.
"""

import os

# Try to import autogen, fall back gracefully if not available
try:
    from autogen import register_function, GroupChat, GroupChatManager
    AUTOGEN_AVAILABLE = True
except ImportError:
    AUTOGEN_AVAILABLE = False
    print("[AutoGen] Warning: pyautogen not available or incompatible with current Python version")

from app.rag.retriever import TaxRetriever
from .tax_expert import create_tax_expert
from .orchestrator import create_orchestrator
from .compliance_agent import create_compliance_agent

# Initialize Retriever
retriever = TaxRetriever()

async def run_autogen_chat(user_message: str, broadcast_callback=None):
    """
    Runs the AutoGen chat flow for a given user message.
    Returns the final response from the TaxExpert.
    
    Falls back to simple RAG response if autogen is not available.
    """
    
    # If autogen is not available, use simple fallback
    if not AUTOGEN_AVAILABLE:
        docs = retriever.retrieve(user_message)
        context = "\n\n".join(docs) if docs else "No relevant tax rules found."
        return f"[Simple Mode] Tax Information:\n\n{context}\n\nNote: AutoGen agents are not available. Using basic RAG retrieval."
    
    llm_config = {
        "config_list": [{
            "model": "gpt-4",
            "api_key": os.getenv("OPENAI_API_KEY")
        }],
        "temperature": 0
    }
    
    tax_expert = create_tax_expert(llm_config)
    orchestrator = create_orchestrator(llm_config)
    compliance_officer = create_compliance_agent(llm_config)
    
    # Define tool with callback access
    def consult_tax_rules(query: str) -> str:
        """
        Searches the tax rules database for relevant information.
        Args:
            query: The search query string.
        Returns:
            A string containing the relevant tax rules.
        """
        print(f"[RAG] Searching for: {query}")
        
        # Stream log if callback exists
        if broadcast_callback:
            import asyncio
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(broadcast_callback({
                    "sender": "tool_log",
                    "message": f"Searching tax rules for: {query}",
                    "type": "info"
                }))
            except RuntimeError:
                pass

        docs = retriever.retrieve(query)
        if not docs:
            return "No relevant tax rules found."
        return "\n\n".join(docs)

    # Register the tool
    # TaxExpert calls the tool, Orchestrator executes it
    register_function(
        consult_tax_rules,
        caller=tax_expert,
        executor=orchestrator,
        name="consult_tax_rules",
        description="Search the tax rules database for relevant information."
    )
    
    # Hook for streaming "thoughts"
    def print_callback(recipient, messages, sender, config):
        if broadcast_callback:
            last_msg = messages[-1]
            content = last_msg.get("content", "")
            if content and "TERMINATE" not in content:
                # We need to schedule the broadcast
                import asyncio
                try:
                    loop = asyncio.get_running_loop()
                    loop.create_task(broadcast_callback({
                        "sender": "agent_log",
                        "message": f"{sender.name}: {content[:100]}...", # Truncate for log
                        "type": "info"
                    }))
                except RuntimeError:
                    pass
        return False, None

    # Register callbacks
    tax_expert.register_reply([orchestrator, None], print_callback, position=0)
    compliance_officer.register_reply([orchestrator, None], print_callback, position=0)
    orchestrator.register_reply([tax_expert, compliance_officer, None], print_callback, position=0)
    
    groupchat = GroupChat(
        agents=[orchestrator, tax_expert, compliance_officer],
        messages=[],
        max_round=10
    )
    manager = GroupChatManager(groupchat=groupchat, llm_config=llm_config)
    
    # Initiate Chat
    # We initiate chat with the Manager
    chat_result = await orchestrator.a_initiate_chat(
        manager,
        message=user_message,
        summary_method="last_msg"
    )
    
    return chat_result.summary
