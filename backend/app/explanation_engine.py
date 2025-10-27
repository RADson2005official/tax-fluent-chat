from typing import Dict, List, Optional
from enum import Enum
from pydantic import BaseModel

class ExpertiseLevel(str, Enum):
    NOVICE = "novice"
    EXPERT = "expert"

class ExplanationRequest(BaseModel):
    """Request model for explanation generation"""
    topic: str
    context: Dict
    expertise_level: ExpertiseLevel = ExpertiseLevel.NOVICE

class Explanation(BaseModel):
    """Response model for explanations"""
    title: str
    content: str
    key_points: List[str]
    expertise_level: ExpertiseLevel
    related_topics: List[str] = []

class ExplanationEngine:
    """
    Explanation engine that generates responses tailored to novice or expert users
    """
    
    # Tax explanation templates
    EXPLANATIONS = {
        "standard_deduction": {
            "novice": {
                "title": "What is the Standard Deduction?",
                "content": (
                    "The standard deduction is a fixed amount that reduces your taxable income. "
                    "Think of it as the government saying 'we won't tax the first $X of your income.' "
                    "It's automatic and you don't need to itemize your expenses to get it."
                ),
                "key_points": [
                    "Reduces your taxable income automatically",
                    "No need to track expenses",
                    "Amount varies by filing status",
                    "Most taxpayers use this instead of itemizing"
                ],
                "related_topics": ["itemized_deductions", "filing_status", "taxable_income"]
            },
            "expert": {
                "title": "Standard Deduction - 2024",
                "content": (
                    "Standard deduction provisions under IRC §63(c). "
                    "Indexed annually for inflation per §63(c)(4). "
                    "Taxpayers may elect to itemize under §63(e) if itemized deductions exceed standard amount."
                ),
                "key_points": [
                    "Single: $14,600",
                    "MFJ: $29,200",
                    "HOH: $21,900",
                    "Additional amount for 65+ or blind: $1,550 ($1,950 single)",
                    "Limitation for dependents: greater of $1,300 or earned income + $450"
                ],
                "related_topics": ["schedule_a", "irc_63", "agi_calculation"]
            }
        },
        "tax_brackets": {
            "novice": {
                "title": "Understanding Tax Brackets",
                "content": (
                    "The U.S. uses a progressive tax system with different brackets. "
                    "You don't pay the same rate on all your income - you pay different rates on different portions. "
                    "For example, the first $11,600 might be taxed at 10%, the next portion at 12%, and so on. "
                    "Your 'marginal rate' is the rate on your last dollar earned."
                ),
                "key_points": [
                    "Only the money in each bracket is taxed at that rate",
                    "Lower income is always taxed at lower rates",
                    "Moving to a higher bracket doesn't increase tax on previous income",
                    "Marginal rate ≠ effective rate"
                ],
                "related_topics": ["marginal_rate", "effective_rate", "taxable_income"]
            },
            "expert": {
                "title": "Tax Rate Schedules - IRC §1",
                "content": (
                    "Progressive marginal rate structure under IRC §1(a)-(d). "
                    "Seven brackets ranging from 10% to 37%. "
                    "Brackets indexed for inflation annually. "
                    "Qualified dividends and LTCG taxed under preferential rates §1(h)."
                ),
                "key_points": [
                    "10%, 12%, 22%, 24%, 32%, 35%, 37%",
                    "Bracket thresholds vary by filing status",
                    "AMT considerations under §55",
                    "NIIT applies at 3.8% above threshold",
                    "Capital gains preferential rates: 0%, 15%, 20%"
                ],
                "related_topics": ["amt", "niit", "capital_gains", "qualified_dividends"]
            }
        },
        "credits": {
            "novice": {
                "title": "Tax Credits: Direct Reductions",
                "content": (
                    "Tax credits are like gift cards for your taxes - they reduce your tax bill dollar-for-dollar. "
                    "If you owe $2,000 in taxes and have a $1,000 credit, you only pay $1,000. "
                    "Some credits are refundable (you can get money back even if you owe no tax) "
                    "and others are non-refundable (they can only reduce your tax to zero)."
                ),
                "key_points": [
                    "Dollar-for-dollar reduction in tax owed",
                    "Better than deductions (which only reduce taxable income)",
                    "Refundable credits can give you money back",
                    "Common credits: Child Tax Credit, EITC, Education credits"
                ],
                "related_topics": ["child_tax_credit", "eitc", "education_credits"]
            },
            "expert": {
                "title": "Tax Credits - IRC §§21-54",
                "content": (
                    "Comprehensive credit provisions spanning multiple IRC sections. "
                    "Credits apply after tax calculation and are subject to various limitations, "
                    "phase-outs, and ordering rules under §26."
                ),
                "key_points": [
                    "CTC: §24, up to $2,000 per child, $1,600 refundable (ACTC)",
                    "EITC: §32, refundable, income and dependent requirements",
                    "Education: §25A (AOTC/LLC), basis adjustment considerations",
                    "General business credit: §38, carryforward/carryback rules",
                    "Credit limitation: §26, regular tax liability constraint"
                ],
                "related_topics": ["form_8812", "form_8863", "schedule_3", "amt_credit"]
            }
        },
        "filing_status": {
            "novice": {
                "title": "Choosing Your Filing Status",
                "content": (
                    "Your filing status determines your tax rates and deduction amounts. "
                    "It's based on your marital status and family situation on December 31st. "
                    "The five statuses are: Single, Married Filing Jointly, Married Filing Separately, "
                    "Head of Household, and Qualifying Surviving Spouse."
                ),
                "key_points": [
                    "Determined by status on last day of tax year",
                    "Married Filing Jointly usually most beneficial for married couples",
                    "Head of Household requires qualifying dependent",
                    "Can't change status after filing (usually)"
                ],
                "related_topics": ["standard_deduction", "tax_brackets", "head_of_household"]
            },
            "expert": {
                "title": "Filing Status - IRC §1 & §2",
                "content": (
                    "Filing status determination under §§1(a)-(d) and §2. "
                    "Status affects rate schedules, phase-out thresholds, and benefit eligibility. "
                    "HOH requires maintenance of household and qualifying person test."
                ),
                "key_points": [
                    "MFJ: §1(a), joint and several liability under §6013(d)(3)",
                    "Surviving spouse: §2(a), two-year benefit post-spouse death",
                    "HOH: §1(b), more than half cost of maintaining household",
                    "MFS: §1(d), special limitations (IRA, credits, deductions)",
                    "Marital status determined under state law at year-end"
                ],
                "related_topics": ["innocent_spouse", "community_property", "mfj_election"]
            }
        }
    }
    
    def generate_explanation(self, request: ExplanationRequest) -> Explanation:
        """
        Generate an explanation tailored to the user's expertise level
        
        Args:
            request: ExplanationRequest with topic and expertise level
            
        Returns:
            Explanation object with content appropriate for the user
            
        Raises:
            ValueError: If topic not found
        """
        topic = request.topic.lower()
        
        if topic not in self.EXPLANATIONS:
            # Generate a generic explanation if topic not found
            return self._generate_generic_explanation(request)
        
        level = request.expertise_level.value
        explanation_data = self.EXPLANATIONS[topic][level]
        
        return Explanation(
            title=explanation_data["title"],
            content=explanation_data["content"],
            key_points=explanation_data["key_points"],
            expertise_level=request.expertise_level,
            related_topics=explanation_data.get("related_topics", [])
        )
    
    def _generate_generic_explanation(self, request: ExplanationRequest) -> Explanation:
        """Generate a generic explanation for unknown topics"""
        if request.expertise_level == ExpertiseLevel.NOVICE:
            return Explanation(
                title=f"About {request.topic.title()}",
                content=(
                    f"We're gathering information about {request.topic}. "
                    "This is a tax-related topic that affects your return. "
                    "Please consult the IRS website or a tax professional for specific guidance."
                ),
                key_points=[
                    "Topic may affect your tax calculation",
                    "Consult IRS Publication 17 for details",
                    "Consider speaking with a tax professional"
                ],
                expertise_level=request.expertise_level,
                related_topics=[]
            )
        else:
            return Explanation(
                title=f"{request.topic.upper()} - Tax Topic",
                content=(
                    f"Tax topic: {request.topic}. "
                    "Refer to relevant IRC sections and Treasury Regulations. "
                    "Review recent case law and IRS guidance for current interpretation."
                ),
                key_points=[
                    "Check applicable IRC sections",
                    "Review Treasury Regulations",
                    "Consider recent court decisions",
                    "Verify current IRS guidance"
                ],
                expertise_level=request.expertise_level,
                related_topics=[]
            )
    
    def get_available_topics(self) -> List[str]:
        """Get list of available explanation topics"""
        return list(self.EXPLANATIONS.keys())

# Create engine instance
explanation_engine = ExplanationEngine()
