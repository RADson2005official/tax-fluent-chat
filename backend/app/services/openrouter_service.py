"""
OpenRouter AI Service
=====================
Provides AI-powered extraction using OpenRouter API with mistralai/devstral-2512 model.
Used as a fallback when pattern matching fails in conversational filing.
"""

import os
import httpx
from typing import Optional, Dict, Any
import json

# OpenRouter configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "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")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_MODEL = "mistralai/devstral-2505"  # Using devstral model


class OpenRouterService:
    """Service for AI-powered extraction and assistance using OpenRouter."""
    
    def __init__(self):
        self.api_key = OPENROUTER_API_KEY
        self.base_url = OPENROUTER_BASE_URL
        self.model = DEFAULT_MODEL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8080",
            "X-Title": "TaxFluent Tax Filing System"
        }
    
    async def extract_value(self, user_message: str, field_type: str, question_context: str) -> Optional[str]:
        """
        Use AI to extract a specific value from user's conversational message.
        
        Args:
            user_message: The user's response
            field_type: Type of field to extract (name, pan, email, salary, etc.)
            question_context: The question that was asked
            
        Returns:
            Extracted value or None if extraction fails
        """
        system_prompt = f"""You are a data extraction assistant for a tax filing system. 
Your task is to extract the {field_type} from the user's message.

Rules:
1. Extract ONLY the requested value, nothing else
2. For amounts, convert to numeric format (e.g., "5 lakh" -> 500000, "8L" -> 800000)
3. For names, extract the full name properly capitalized
4. For PAN, extract in uppercase format ABCDE1234F
5. For email, extract the email address
6. If the user says "no", "none", "nil", "skip" - return "SKIP"
7. If you cannot find the value, return "NOT_FOUND"
8. Return ONLY the extracted value, no explanation

Field type to extract: {field_type}
Question that was asked: {question_context}"""

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": f"Extract the {field_type} from this message: \"{user_message}\""}
                        ],
                        "temperature": 0.1,
                        "max_tokens": 100
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    extracted = data["choices"][0]["message"]["content"].strip()
                    
                    # Clean up the response
                    extracted = extracted.strip('"\'')
                    
                    if extracted in ["NOT_FOUND", "SKIP"]:
                        return extracted if extracted == "SKIP" else None
                    
                    return extracted
                else:
                    print(f"[OpenRouter] API error: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            print(f"[OpenRouter] Extraction error: {e}")
            return None
    
    async def generate_response(self, user_message: str, context: str = "") -> str:
        """
        Generate a conversational response for tax-related queries.
        """
        system_prompt = """You are an Expert Chartered Accountant (CA) helping users file their taxes.
You are friendly, professional, and helpful.
Provide clear, concise responses about Indian tax filing.
If the user provides information, acknowledge it and ask the next relevant question."""

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": f"Context: {context}\n\nUser message: {user_message}"}
                        ],
                        "temperature": 0.7,
                        "max_tokens": 300
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data["choices"][0]["message"]["content"].strip()
                else:
                    return "I apologize, I'm having trouble processing your request. Please try again."
                    
        except Exception as e:
            print(f"[OpenRouter] Response error: {e}")
            return "I apologize, there was an error. Please try again."
    
    async def parse_amount(self, text: str) -> Optional[float]:
        """
        Use AI to parse any format of amount into a number.
        """
        system_prompt = """You are a number parser. Convert the given text into a numeric amount in Indian Rupees.
Examples:
- "5 lakh" -> 500000
- "8L" -> 800000
- "₹800000" -> 800000
- "8,00,000" -> 800000
- "eight lakhs" -> 800000
- "5 crore" -> 50000000

Return ONLY the number, nothing else. If you can't parse it, return 0."""

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": f"Convert to number: {text}"}
                        ],
                        "temperature": 0,
                        "max_tokens": 50
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    result = data["choices"][0]["message"]["content"].strip()
                    # Clean and parse
                    result = result.replace(",", "").replace(" ", "")
                    return float(result)
                    
        except Exception as e:
            print(f"[OpenRouter] Parse amount error: {e}")
            
        return None


# Singleton instance
_openrouter_service: Optional[OpenRouterService] = None


def get_openrouter_service() -> OpenRouterService:
    """Get or create OpenRouter service instance."""
    global _openrouter_service
    if _openrouter_service is None:
        _openrouter_service = OpenRouterService()
    return _openrouter_service
