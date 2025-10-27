"""
Explanation Engine - Task C
Generates adaptive responses for novice/intermediate/expert users
"""

from typing import Dict, List


class ExplanationEngine:
    """
    Generates context-aware explanations adapted to user proficiency level
    """
    
    # Tax terminology database with multi-level explanations
    TAX_TERMS = {
        "agi": {
            "novice": "AGI (Adjusted Gross Income) is your total income minus certain deductions. Think of it as your income after some allowed subtractions, but before the standard or itemized deductions.",
            "intermediate": "AGI is your gross income adjusted by specific deductions like educator expenses, student loan interest, and IRA contributions. It's a key number used to determine eligibility for many tax benefits.",
            "expert": "AGI = Gross Income - Above-the-line deductions (Schedule 1 adjustments). Critical threshold for phase-outs of credits (EITC, CTC, etc.) and deduction limitations (SALT cap impact)."
        },
        "standard_deduction": {
            "novice": "The standard deduction is an amount the IRS lets you subtract from your income without needing receipts. Most people use this instead of itemizing.",
            "intermediate": "The standard deduction is a fixed amount based on filing status that reduces taxable income. For 2024: $14,600 (single), $29,200 (married joint), $21,900 (head of household). Use if it exceeds itemized deductions.",
            "expert": "2024 standard deductions indexed to inflation. Compare against Schedule A itemized total (SALT capped at $10K, mortgage interest, charitable contributions). Additional amounts for age 65+ and blind taxpayers."
        },
        "marginal_rate": {
            "novice": "Your marginal tax rate is the percentage of tax you pay on your next dollar of income. It's the highest tax bracket you reach.",
            "intermediate": "The marginal rate is the tax rate applied to your last dollar of taxable income. Due to progressive brackets, you pay different rates on different portions of income.",
            "expert": "Marginal rate = highest bracket reached. Critical for tax planning: LTCG rate transitions at bracket thresholds, IRMAA Medicare surcharge triggers, and optimal timing for income recognition/deduction acceleration."
        },
        "effective_rate": {
            "novice": "Your effective tax rate is the overall percentage of your income that goes to taxes. It's usually lower than your marginal rate because of how tax brackets work.",
            "intermediate": "Effective rate = Total tax / Gross income. Always lower than marginal rate due to progressive brackets. Useful metric for comparing tax burden across income levels or years.",
            "expert": "Effective rate calculation: Fed tax liability / AGI. More accurate metric than marginal for multi-year planning. Consider phase-in/phase-out regions where effective marginal rates can exceed statutory rates."
        },
        "itemized_deductions": {
            "novice": "Itemized deductions let you list specific expenses (like mortgage interest, charitable donations, medical expenses) to reduce your taxable income. Only worth it if they exceed your standard deduction.",
            "intermediate": "Schedule A deductions including mortgage interest, state/local taxes (SALT, capped at $10K), medical expenses >7.5% AGI, and charitable contributions. Beneficial when total exceeds standard deduction.",
            "expert": "Post-TCJA landscape: SALT cap makes itemizing harder for high-tax states. Bunching strategy for charitable contributions. Medical expense threshold at 7.5% AGI. Mortgage interest limited to $750K principal (acquisition debt)."
        },
        "progressive_brackets": {
            "novice": "Tax brackets mean you pay different rates on different portions of your income. As you earn more, only the extra money is taxed at the higher rate, not all your income.",
            "intermediate": "U.S. uses marginal tax brackets: income is taxed in layers. 2024 has 7 brackets (10%, 12%, 22%, 24%, 32%, 35%, 37%). Each bracket applies only to income within that range.",
            "expert": "Progressive structure creates non-linear effective rates. Planning opportunities at bracket boundaries: Roth conversions, capital gain harvesting, income shifting. Beware of 'bubbles' where effective marginal exceeds statutory due to phase-outs."
        },
        "credits": {
            "novice": "Tax credits are better than deductions—they directly reduce the tax you owe, dollar-for-dollar. Some credits like the Child Tax Credit or Earned Income Credit can be very valuable.",
            "intermediate": "Credits reduce tax liability directly (vs. deductions that reduce taxable income). Key credits: CTC ($2,000/child), EITC (income-based), education credits (AOTC, LLC), dependent care, energy credits.",
            "expert": "Refundable vs. non-refundable distinction critical. Phase-out ranges create high effective marginal rates. CTC phase-out starts at $400K (MFJ). EITC optimization requires careful income management. Coordinate with AMT for some credits."
        }
    }
    
    # Common tax topics and their explanations
    TOPICS = {
        "filing_status": {
            "novice": "Your filing status (like Single, Married Filing Jointly, or Head of Household) affects your tax brackets and standard deduction. Choose the one that fits your situation—usually the one that gives you the lowest tax.",
            "intermediate": "Filing status determines standard deduction amounts and bracket thresholds. Options: Single, Married Filing Jointly, Married Filing Separately, Head of Household, Qualifying Widow(er). Consider marriage bonus/penalty.",
            "expert": "Filing status optimization: MFJ vs. MFS analysis for SALT cap, student loan interest, IRA phase-outs. HOH requirements: maintain home for qualifying person >50% of year. QSS status limited to 2 years post-spouse death."
        },
        "deductions_vs_credits": {
            "novice": "Deductions lower your taxable income (how much income gets taxed), while credits lower your actual tax bill. A $1,000 credit saves you $1,000 in taxes, but a $1,000 deduction saves you less (based on your tax rate).",
            "intermediate": "Deductions reduce taxable income (value = deduction × marginal rate). Credits reduce tax owed dollar-for-dollar. $1,000 credit > $1,000 deduction. Some credits are refundable (can create refund).",
            "expert": "Optimization hierarchy: refundable credits > non-refundable credits > deductions. AMT eliminates many deductions but not all credits. Timing strategies differ: accelerate deductions into high-income years, spread credits if phase-out applies."
        },
        "tax_planning": {
            "novice": "Tax planning means making smart choices throughout the year to reduce your taxes legally. This includes timing income and expenses, maximizing deductions and credits, and contributing to retirement accounts.",
            "intermediate": "Year-round strategies: maximize retirement contributions (401k, IRA), HSA funding, timing of income/deductions, capital gain/loss harvesting, charitable giving strategies, education savings (529 plans).",
            "expert": "Multi-year planning framework: project income streams, optimize bracket management, Roth conversion ladders, installment sale elections, depreciation strategies, NOL carryforward/carryback. Consider state tax impacts and AMT planning."
        }
    }
    
    @staticmethod
    def get_explanation(
        query: str,
        proficiency: str = "novice",
        context: Dict = None
    ) -> Dict[str, any]:
        """
        Generate an adaptive explanation based on user query and proficiency
        
        Args:
            query: The user's question or topic
            proficiency: User's proficiency level (novice/intermediate/expert)
            context: Additional context (e.g., tax calculation results)
            
        Returns:
            Dictionary with explanation and metadata
        """
        if proficiency not in ["novice", "intermediate", "expert"]:
            proficiency = "novice"
        
        query_lower = query.lower()
        
        # Check if query matches a specific term
        for term, explanations in ExplanationEngine.TAX_TERMS.items():
            if term.replace("_", " ") in query_lower or term in query_lower:
                return {
                    "explanation": explanations[proficiency],
                    "proficiency": proficiency,
                    "technical_terms": ExplanationEngine._extract_terms(explanations[proficiency]),
                    "related_topics": ExplanationEngine._get_related_topics(term)
                }
        
        # Check if query matches a topic
        for topic, explanations in ExplanationEngine.TOPICS.items():
            if topic.replace("_", " ") in query_lower:
                return {
                    "explanation": explanations[proficiency],
                    "proficiency": proficiency,
                    "technical_terms": ExplanationEngine._extract_terms(explanations[proficiency]),
                    "related_topics": ExplanationEngine._get_related_topics(topic)
                }
        
        # If context includes tax calculation, provide explanation based on that
        if context and "federal_tax" in context:
            return ExplanationEngine._explain_calculation(context, proficiency)
        
        # Default response
        return {
            "explanation": ExplanationEngine._get_default_explanation(query, proficiency),
            "proficiency": proficiency,
            "technical_terms": [],
            "related_topics": ["tax_planning", "filing_status"]
        }
    
    @staticmethod
    def _explain_calculation(context: Dict, proficiency: str) -> Dict[str, any]:
        """Generate explanation for a tax calculation result"""
        income = context.get("gross_income", 0)
        tax = context.get("federal_tax", 0)
        effective = context.get("effective_rate", 0)
        marginal = context.get("marginal_rate", 0)
        
        if proficiency == "novice":
            explanation = (
                f"Your federal tax is ${tax:,.2f} on income of ${income:,.2f}. "
                f"That's an effective rate of {effective:.1f}%, meaning that percentage of your income goes to federal taxes. "
                f"Your marginal rate is {marginal:.0f}%, which is the rate on your next dollar earned."
            )
        elif proficiency == "intermediate":
            explanation = (
                f"Tax calculation: ${income:,.2f} gross income resulted in ${tax:,.2f} federal tax liability. "
                f"Effective rate: {effective:.1f}% (total tax / gross income). "
                f"Marginal rate: {marginal:.0f}% (bracket for next dollar). "
                f"The difference illustrates the progressive bracket structure."
            )
        else:  # expert
            explanation = (
                f"Tax liability: ${tax:,.2f} on AGI ${income:,.2f} (effective rate: {effective:.1f}%). "
                f"Marginal bracket: {marginal:.0f}%. "
                f"Note: effective marginal rate may differ due to phase-outs. "
                f"Consider: LTCG rate positioning, AMT calculation, state tax interactions."
            )
        
        return {
            "explanation": explanation,
            "proficiency": proficiency,
            "technical_terms": ["effective_rate", "marginal_rate", "progressive_brackets"],
            "related_topics": ["tax_planning", "deductions_vs_credits"]
        }
    
    @staticmethod
    def _get_default_explanation(query: str, proficiency: str) -> str:
        """Provide a helpful default response"""
        if proficiency == "novice":
            return (
                "I can help explain tax concepts! Try asking about topics like: "
                "tax brackets, deductions, credits, filing status, or AGI. "
                "I'll explain everything in simple terms."
            )
        elif proficiency == "intermediate":
            return (
                "I can provide detailed explanations on tax topics including: "
                "progressive brackets, itemized vs. standard deductions, tax credits, "
                "filing status optimization, and tax planning strategies."
            )
        else:  # expert
            return (
                "Available for detailed technical analysis: bracket management, "
                "AMT planning, phase-out optimization, multi-year tax strategies, "
                "entity structure, depreciation methods, and advanced credit coordination."
            )
    
    @staticmethod
    def _extract_terms(text: str) -> List[str]:
        """Extract key tax terms from explanation text"""
        terms = []
        term_keywords = ["AGI", "deduction", "credit", "bracket", "rate", "income", "itemized", "standard"]
        
        for keyword in term_keywords:
            if keyword.lower() in text.lower():
                terms.append(keyword.lower())
        
        return list(set(terms))[:5]  # Return up to 5 unique terms
    
    @staticmethod
    def _get_related_topics(term: str) -> List[str]:
        """Get related topics for a given term"""
        related = {
            "agi": ["standard_deduction", "itemized_deductions", "credits"],
            "standard_deduction": ["itemized_deductions", "agi", "filing_status"],
            "marginal_rate": ["effective_rate", "progressive_brackets", "tax_planning"],
            "effective_rate": ["marginal_rate", "progressive_brackets"],
            "itemized_deductions": ["standard_deduction", "agi", "deductions_vs_credits"],
            "progressive_brackets": ["marginal_rate", "effective_rate", "tax_planning"],
            "credits": ["deductions_vs_credits", "agi", "tax_planning"],
            "filing_status": ["standard_deduction", "progressive_brackets", "tax_planning"],
            "deductions_vs_credits": ["credits", "itemized_deductions", "tax_planning"],
            "tax_planning": ["deductions_vs_credits", "credits", "marginal_rate"]
        }
        
        return related.get(term, ["tax_planning", "filing_status"])[:3]


def explain(query: str, proficiency: str = "novice", context: Dict = None) -> Dict:
    """
    Convenience function to generate explanations
    
    Args:
        query: User's question
        proficiency: User proficiency level
        context: Additional context
        
    Returns:
        Explanation dictionary
    """
    return ExplanationEngine.get_explanation(query, proficiency, context)
