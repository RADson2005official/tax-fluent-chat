"""
LLaMA Tax Expert Service
========================
Loads and manages the fine-tuned LLaMA 3.2 model for tax-related conversations.
Optimized for GTX 1650Ti (4GB VRAM) with 4-bit quantization and CPU offloading.
"""

import os
import torch
from typing import Optional, Generator, Dict, Any
from functools import lru_cache

# Model configuration - using pre-quantized unsloth model (fits in 4GB VRAM)
# For GPU+CPU hybrid, would need non-quantized model, but that requires more VRAM
BASE_MODEL = "unsloth/llama-3-8b-Instruct-bnb-4bit"  # Pre-quantized, GPU-only
PEFT_MODEL = "JayNagose/LLaMa-3.2-tax-basic"

# Tax Expert system prompt
TAX_EXPERT_SYSTEM_PROMPT = """You are an Expert Chartered Accountant (CA) specialized in Indian tax law and filing systems. 
Your role is to:
1. Help users understand their tax obligations
2. Extract tax-relevant information from conversations
3. Guide users through the tax filing process
4. Provide accurate information about deductions, exemptions, and tax calculations

When users share income or financial details, acknowledge them and ask follow-up questions to gather complete information for their tax return.

Always be professional, accurate, and helpful. If you're unsure about something, say so rather than guessing."""

class LlamaTaxExpert:
    """LLaMA-based Tax Expert for conversational tax assistance."""
    
    _instance: Optional['LlamaTaxExpert'] = None
    _model = None
    _tokenizer = None
    _is_loaded = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        self.device = self._get_device()
        self.max_new_tokens = 512
        self.conversation_history: list = []
        
    def _get_device(self) -> str:
        """Detect available device (GPU/CPU)."""
        if torch.cuda.is_available():
            # Check VRAM - GTX 1650Ti has 4GB
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
            print(f"[LLaMA] GPU detected: {torch.cuda.get_device_name(0)} with {gpu_memory:.1f}GB VRAM")
            return "cuda"
        else:
            print("[LLaMA] No GPU detected, using CPU (slower inference)")
            return "cpu"
    
    def load_model(self) -> bool:
        """Load the model with PEFT adapter. Returns True if successful."""
        if self._is_loaded:
            return True
            
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
            from peft import PeftModel
            
            print(f"[LLaMA] Loading base model: {BASE_MODEL}")
            
            # GPU-only mode with pre-quantized 4-bit model
            # Note: Pre-quantized model doesn't support CPU offload - runs entirely on GPU
            # The unsloth 4-bit model fits in ~4GB VRAM
            bnb_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_use_double_quant=True,
                bnb_4bit_compute_dtype=torch.float16
            )
            
            # Load tokenizer
            self._tokenizer = AutoTokenizer.from_pretrained(
                BASE_MODEL,
                trust_remote_code=True,
                use_fast=True
            )
            if self._tokenizer.pad_token is None:
                self._tokenizer.pad_token = self._tokenizer.eos_token
            
            # Load base model - GPU only for pre-quantized model
            if torch.cuda.is_available():
                gpu_name = torch.cuda.get_device_name(0)
                gpu_memory_gb = torch.cuda.get_device_properties(0).total_memory / (1024**3)
                print(f"[LLaMA] Loading on GPU: {gpu_name} ({gpu_memory_gb:.1f}GB VRAM)")
                device_map = "cuda"
            else:
                print("[LLaMA] Loading on CPU (slower inference)")
                device_map = "cpu"
            
            print("[LLaMA] Loading with 4-bit quantization...")
            self._model = AutoModelForCausalLM.from_pretrained(
                BASE_MODEL,
                quantization_config=bnb_config if torch.cuda.is_available() else None,
                device_map=device_map,
                torch_dtype=torch.float16,
                trust_remote_code=True,
                low_cpu_mem_usage=True
            )
            
            # Apply PEFT adapter
            print(f"[LLaMA] Applying PEFT adapter: {PEFT_MODEL}")
            self._model = PeftModel.from_pretrained(
                self._model,
                PEFT_MODEL,
                torch_dtype=torch.float16
            )
            
            self._model.eval()
            self._is_loaded = True
            print("[LLaMA] Model loaded successfully!")
            return True
            
        except Exception as e:
            print(f"[LLaMA] Error loading model: {e}")
            return False
    
    def format_prompt(self, user_message: str, include_history: bool = True) -> str:
        """Format prompt with conversation history for LLaMA instruct format."""
        messages = []
        
        # System message
        messages.append({"role": "system", "content": TAX_EXPERT_SYSTEM_PROMPT})
        
        # Add conversation history
        if include_history:
            for msg in self.conversation_history[-6:]:  # Keep last 6 exchanges
                messages.append(msg)
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        # Format for LLaMA 3 Instruct
        formatted = ""
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            if role == "system":
                formatted += f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n{content}<|eot_id|>"
            elif role == "user":
                formatted += f"<|start_header_id|>user<|end_header_id|>\n\n{content}<|eot_id|>"
            elif role == "assistant":
                formatted += f"<|start_header_id|>assistant<|end_header_id|>\n\n{content}<|eot_id|>"
        
        formatted += "<|start_header_id|>assistant<|end_header_id|>\n\n"
        return formatted
    
    def generate(self, user_message: str, stream: bool = False) -> str:
        """Generate response for user message."""
        if not self._is_loaded:
            if not self.load_model():
                return "Sorry, I'm having trouble loading the AI model. Please try again later."
        
        try:
            prompt = self.format_prompt(user_message)
            
            inputs = self._tokenizer(
                prompt,
                return_tensors="pt",
                truncation=True,
                max_length=2048
            ).to(self.device)
            
            with torch.no_grad():
                outputs = self._model.generate(
                    **inputs,
                    max_new_tokens=self.max_new_tokens,
                    temperature=0.7,
                    top_p=0.9,
                    do_sample=True,
                    pad_token_id=self._tokenizer.pad_token_id,
                    eos_token_id=self._tokenizer.eos_token_id,
                )
            
            # Decode response
            response = self._tokenizer.decode(
                outputs[0][inputs['input_ids'].shape[1]:],
                skip_special_tokens=True
            ).strip()
            
            # Update conversation history
            self.conversation_history.append({"role": "user", "content": user_message})
            self.conversation_history.append({"role": "assistant", "content": response})
            
            return response
            
        except Exception as e:
            print(f"[LLaMA] Generation error: {e}")
            return f"I encountered an error processing your request: {str(e)}"
    
    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []
    
    def get_history(self) -> list:
        """Get conversation history."""
        return self.conversation_history.copy()
    
    @property
    def is_loaded(self) -> bool:
        return self._is_loaded


# Singleton accessor
@lru_cache(maxsize=1)
def get_llama_expert() -> LlamaTaxExpert:
    """Get or create the LLaMA Tax Expert instance."""
    return LlamaTaxExpert()


async def generate_llama_response(user_message: str, session_id: str = "default") -> Dict[str, Any]:
    """
    Async wrapper for generating LLaMA responses.
    Used by API endpoints.
    """
    expert = get_llama_expert()
    response = expert.generate(user_message)
    
    return {
        "response": response,
        "session_id": session_id,
        "conversation_length": len(expert.conversation_history)
    }
