from autogen import AssistantAgent

def create_form_filler(llm_config: dict) -> AssistantAgent:
    return AssistantAgent(
        name="FormFiller",
        system_message="""You are a Form Filler Agent for a tax filing system.
        Your responsibility is to review the aggregated tax data (W-2s, 1099s, personal info) and verify if it is sufficient to generate a tax return.
        
        Rules:
        1. Check if personal info (name, email) is present.
        2. Check if at least one income source (W-2 or 1099) is present.
        3. Check if filing status is present.
        
        If data is missing, list the missing items.
        If data is sufficient, reply with "APPROVED".
        """,
        llm_config=llm_config
    )
