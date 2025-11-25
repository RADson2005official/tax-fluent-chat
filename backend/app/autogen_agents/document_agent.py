from autogen import AssistantAgent
import json

def create_document_agent(llm_config):
    agent = AssistantAgent(
        name="DocumentProcessor",
        system_message="""You are a Document Processing Agent.
        Your job is to take raw text extracted from tax documents (W-2, 1099) and parse it into structured JSON.
        
        Output ONLY valid JSON. Do not add markdown formatting or explanations.
        
        Structure for W-2:
        {
            "form_type": "W-2",
            "employer_name": "...",
            "employer_ein": "...",
            "wages_tips_other_compensation": 0.0,
            "federal_income_tax_withheld": 0.0,
            "social_security_wages": 0.0,
            "social_security_tax_withheld": 0.0,
            "medicare_wages_and_tips": 0.0,
            "medicare_tax_withheld": 0.0,
            "tax_year": 2024
        }
        
        Structure for 1099-NEC:
        {
            "form_type": "1099-NEC",
            "payer_name": "...",
            "payer_tin": "...",
            "nonemployee_compensation": 0.0,
            "federal_income_tax_withheld": 0.0
        }
        
        If the text is unclear or missing data, infer reasonable values or use null.
        """,
        llm_config=llm_config
    )
    return agent
