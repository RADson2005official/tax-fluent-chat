
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from peft import PeftModel, PeftConfig
import os

class TaxLLMService:
    _instance = None
    _model = None
    _tokenizer = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TaxLLMService, cls).__new__(cls)
        return cls._instance

    def initialize(self):
        """Initializes the model and tokenizer if not already loaded."""
        if self._model is not None:
            return

        base_model_name = "unsloth/llama-3-8b-Instruct-bnb-4bit"
        adapter_model_name = "JayNagose/LLaMa-3.2-tax-basic"

        print(f"Loading base model: {base_model_name}")
        
        if torch.cuda.is_available():
            print("CUDA detected. using 4-bit quantization.")
            # BitsAndBytes Configuration for 4-bit loading
            bnb_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_use_double_quant=True,
                bnb_4bit_compute_dtype=torch.float16
            )
            model_kwargs = {"quantization_config": bnb_config, "device_map": "auto"}
        else:
            print("WARNING: GPU/CUDA not detected. 4-bit quantization skipped (requires GPU). Loading in standard precision on CPU. This may use significant RAM.")
            model_kwargs = {"device_map": "cpu", "low_cpu_mem_usage": True}

        try:
            self._tokenizer = AutoTokenizer.from_pretrained(base_model_name)
            
            # Load base model
            base_model = AutoModelForCausalLM.from_pretrained(
                base_model_name,
                trust_remote_code=True,
                **model_kwargs
            )
            
            print(f"Loading adapter: {adapter_model_name}")
            # Load PEFT adapter
            self._model = PeftModel.from_pretrained(base_model, adapter_model_name)
            
            print("Tax LLM loaded successfully.")
            
        except Exception as e:
            print(f"Error loading Tax LLM: {e}")
            raise e

    def generate_response(self, prompt: str, max_new_tokens: int = 512, temperature: float = 0.7) -> str:
        """Generates a response from the model."""
        if self._model is None:
            self.initialize()

        # Format prompt for Llama 3 (Instruct) if needed, or raw text
        # Llama 3 Instruct format: <|begin_of_text|><|start_header_id|>user<|end_header_id|>\n\n{message}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n
        
        formatted_prompt = f"<|begin_of_text|><|start_header_id|>user<|end_header_id|>\n\n{prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n"
        
        inputs = self._tokenizer(formatted_prompt, return_tensors="pt").to(self._model.device)
        
        with torch.no_grad():
            outputs = self._model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                do_sample=True,
                pad_token_id=self._tokenizer.eos_token_id
            )
        
        decoded_output = self._tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract only the assistant's response (removing the prompt)
        # This simple split assumes the model repeats the prompt or we just want the text after the prompt header
        # Ideally, we find the system/user/assistant boundaries
        
        # Simple cleanup for now: remove the prompt part if it's there
        # But tokenizer.decode usually returns everything. 
        # Let's try to split by 'assistant\n\n' if possible or just return full for now and let caller handle
        
        # Better extraction for Llama 3
        try:
             response = decoded_output.split("assistant\n\n")[-1].strip()
        except:
             response = decoded_output

        return response

tax_llm_service = TaxLLMService()
