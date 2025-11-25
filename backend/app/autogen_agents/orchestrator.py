import os
from autogen import UserProxyAgent

def create_orchestrator(llm_config):
    agent = UserProxyAgent(
        name="Orchestrator",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=5,
        code_execution_config={"work_dir": "coding", "use_docker": False},
        system_message="""You are a proxy for the user. You execute tools suggested by the TaxExpert.
        If the TaxExpert asks a question, you can provide the user's input (simulated for now or passed via context).
        """
    )
    return agent
