"""
Server-Driven UI (SDUI) Generator Logic

Contains the business logic to generate UI schemas based on user state and persona.
"""
from typing import Dict, Any, List
from .schema import Screen, UIComponent

def generate_dashboard_schema(user_profile: Dict[str, Any]) -> Screen:
    """
    Generates the dashboard layout based on the user's profile.
    
    Args:
        user_profile: Dictionary containing user data (age, income, etc.)
        
    Returns:
        Screen object defining the UI layout
    """
    age = user_profile.get("age", 30)
    mode = user_profile.get("mode", "standard")
    
    # Use simplified layout for seniors or novice users
    use_simplified = age >= 60 or mode == "novice"
    
    # Common components
    header = UIComponent(
        type="Header",
        props={"title": "Tax Dashboard", "subtitle": f"Welcome back, {user_profile.get('name', 'User')}"}
    )
    
    if use_simplified:
        # Simplified layout for senior citizens
        # Focus on large text, clear actions, and accessibility
        return Screen(
            id="dashboard-senior",
            title="My Tax Dashboard",
            layout="single-column",
            components=[
                header,
                UIComponent(
                    type="Card",
                    props={"title": "Quick Actions", "variant": "glass"},
                    children=[
                        UIComponent(
                            type="Button",
                            props={
                                "label": "Start New Filing",
                                "variant": "primary",
                                "size": "large",
                                "icon": "PlusCircle",
                                "block": True,
                                "route": "/filing/new"
                            }
                        ),
                        UIComponent(
                            type="Button",
                            props={
                                "label": "View Last Year's Return",
                                "variant": "outline",
                                "size": "large",
                                "icon": "FileText",
                                "block": True,
                                "class": "mt-4",
                                "route": "/filings"
                            }
                        )
                    ]
                ),
                UIComponent(
                    type="Card",
                    props={"title": "Need Help?", "variant": "glass", "class": "mt-6"},
                    children=[
                        UIComponent(
                            type="Text",
                            props={"content": "Call our support line or chat with our AI assistant.", "size": "lg"}
                        ),
                        UIComponent(
                            type="Button",
                            props={"label": "Chat with Assistant", "variant": "secondary", "size": "large", "class": "mt-4", "route": "/chat"}
                        )
                    ]
                )
            ]
        )
    else:
        # Dense "Bento Grid" layout for standard users
        # Focus on data visualization and efficiency
        return Screen(
            id="dashboard-standard",
            title="Tax Command Center",
            layout="bento-grid",
            components=[
                # Header
                UIComponent(
                    type="Header",
                    props={
                        "title": "Tax Command Center", 
                        "subtitle": f"Welcome back, {user_profile.get('name', 'User')}",
                        "class": "col-span-full"
                    }
                ),
                # Row 1: Stats
                UIComponent(
                    type="StatCard",
                    props={"label": "Estimated Tax", "value": "₹45,000", "trend": "+12%", "icon": "IndianRupee"}
                ),
                UIComponent(
                    type="StatCard",
                    props={"label": "Deductions Claimed", "value": "₹1.2L", "trend": "Maxed", "icon": "ShieldCheck"}
                ),
                UIComponent(
                    type="StatCard",
                    props={"label": "Filing Status", "value": "Draft", "status": "warning", "icon": "Clock"}
                ),
                
                # Row 2: Main Visualization (Sankey)
                UIComponent(
                    type="Card",
                    props={"title": "Tax Flow Visualization", "class": "col-span-2 row-span-2 glass-card"},
                    children=[
                        UIComponent(type="SankeyDiagram", props={"height": "400px"})
                    ]
                ),
                
                # Row 2: Recent Activity
                UIComponent(
                    type="Card",
                    props={"title": "Recent Activity", "class": "glass-card"},
                    children=[
                        UIComponent(type="ActivityList", props={"limit": 5})
                    ]
                ),
                
                # Row 3: Actions
                UIComponent(
                    type="Card",
                    props={"title": "Actions", "class": "glass-card"},
                    children=[
                        UIComponent(
                            type="Button",
                            props={"label": "Continue Filing", "variant": "primary", "block": True, "route": "/filing/new"}
                        ),
                        UIComponent(
                            type="Button",
                            props={"label": "Upload Documents", "variant": "outline", "block": True, "class": "mt-2", "route": "/documents"}
                        )
                    ]
                )
            ]
        )
