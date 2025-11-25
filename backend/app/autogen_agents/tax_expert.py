import os
from autogen import AssistantAgent

def create_tax_expert(llm_config):
    agent = AssistantAgent(
        name="TaxExpert",
        system_message="""You are a helpful Tax Expert. You answer user questions about tax rules.
        ALWAYS use the 'consult_tax_rules' tool to verify your answers against the latest tax rules.
        Do not guess. If you don't find the answer in the rules, say so.
        Reply TERMINATE when the task is done.""",
        llm_config=llm_config
    )
    return agent
