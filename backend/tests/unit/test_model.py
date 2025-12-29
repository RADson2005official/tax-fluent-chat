
import sys
import os

# Add the backend directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.tax_llm import tax_llm_service

def verify_model():
    print("Initialize Tax LLM verification...")
    try:
        tax_llm_service.initialize()
        
        test_prompt = "What documents do I need for filing taxes in India?"
        print(f"\nGeneratin response for prompt: '{test_prompt}'\n")
        
        response = tax_llm_service.generate_response(test_prompt, max_new_tokens=100)
        
        print("-" * 50)
        print("Model Response:")
        print(response)
        print("-" * 50)
        print("\nVerification Successful: Model loaded and generated text.")
        
    except Exception as e:
        print(f"\nVerification Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verify_model()
