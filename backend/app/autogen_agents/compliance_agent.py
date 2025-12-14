from autogen import AssistantAgent

def create_compliance_agent(llm_config):
    agent = AssistantAgent(
        name="ComplianceOfficer",
        system_message="""You are a strict Compliance Officer.
        Your job is to validate tax returns against non-negotiable rules.
        
        Rules:
        1. PAN and Aadhaar must be linked.
        2. High-value transactions (> 1 Lakh credit card, > 30 Lakh property) must be justified.
        3. Bank account must be pre-validated.
        4. Regime selection (Old vs New) must be consistent with business income rules.
        
        If you find a violation, report it immediately.
        If the TaxExpert proposes a plan, review it for compliance.
        """,
        llm_config=llm_config
    )
    return agent
