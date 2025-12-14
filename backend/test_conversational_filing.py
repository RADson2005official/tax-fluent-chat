"""
QA Test Script for Conversational Tax Filing
=============================================
Automated test that simulates a complete tax filing conversation.
"""

import asyncio
import httpx
import json

API_BASE = "http://localhost:8000/api"

# Test data - simulating a user filling tax return
TEST_RESPONSES = [
    ("Dakshit Vardekar", "name"),  # Name
    ("ABCDE1234F", "pan"),  # PAN
    ("dakshit@gmail.com", "email"),  # Email
    ("Tata Consultancy Services", "employer"),  # Employer
    ("8 lakh", "salary"),  # Salary - testing lakh format
    ("no", "other_income"),  # Other income - skip
    ("150000", "deduction_80c"),  # 80C
    ("25000", "deduction_80d"),  # 80D
    ("15000", "hra"),  # HRA
    ("new", "regime"),  # Tax regime
]


async def run_qa_test():
    """Run the complete QA test."""
    print("=" * 60)
    print("🧪 QA TEST: Conversational Tax Filing")
    print("=" * 60)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # 1. Start a new filing session
        session_id = f"qa_test_{int(asyncio.get_event_loop().time())}"
        print(f"\n📋 Starting session: {session_id}")
        
        start_response = await client.get(f"{API_BASE}/chat/filing/start/{session_id}")
        if start_response.status_code != 200:
            print(f"❌ FAILED: Could not start session - {start_response.text}")
            return False
        
        data = start_response.json()
        print(f"✅ Session started")
        print(f"   Bot: {data['response'][:80]}...")
        print(f"   Progress: {data['progress']}%")
        print(f"   Current Step: {data['current_step']}")
        
        # 2. Process each test response
        for test_input, expected_step in TEST_RESPONSES:
            print(f"\n--- Step: {expected_step} ---")
            print(f"   User: {test_input}")
            
            response = await client.post(
                f"{API_BASE}/chat/filing/respond",
                json={"message": test_input, "session_id": session_id}
            )
            
            if response.status_code != 200:
                print(f"❌ FAILED: API error - {response.text}")
                return False
            
            data = response.json()
            
            # Truncate response for display
            bot_response = data['response']
            if len(bot_response) > 100:
                bot_response = bot_response[:100] + "..."
            
            print(f"   Bot: {bot_response}")
            print(f"   Progress: {data['progress']:.1f}%")
            
            if data.get('extracted_data'):
                print(f"   Extracted Data: {json.dumps(data['extracted_data'], indent=2)[:200]}...")
            
            if data.get('is_complete'):
                print(f"\n🎉 Filing Complete!")
                break
        
        # 3. Verify final state
        print("\n" + "=" * 60)
        print("📊 FINAL VERIFICATION")
        print("=" * 60)
        
        status_response = await client.get(f"{API_BASE}/chat/filing/status/{session_id}")
        if status_response.status_code == 200:
            final_data = status_response.json()
            print(f"✅ Final Progress: {final_data['progress']}%")
            print(f"✅ Is Complete: {final_data['is_complete']}")
            print(f"✅ Extracted Data:")
            print(json.dumps(final_data['extracted_data'], indent=2))
            
            # Validate extracted data
            ed = final_data['extracted_data']
            validations = [
                ("Name", ed.get('personal_info', {}).get('name') == 'Dakshit Vardekar'),
                ("PAN", ed.get('personal_info', {}).get('pan_number') == 'ABCDE1234F'),
                ("Email", ed.get('personal_info', {}).get('email') == 'dakshit@gmail.com'),
                ("Employer", 'tata' in str(ed.get('income', {}).get('employer_name', '')).lower()),
                ("Salary", ed.get('income', {}).get('salary') == 800000),
            ]
            
            print("\n📋 Validation Results:")
            all_passed = True
            for name, passed in validations:
                status = "✅ PASS" if passed else "❌ FAIL"
                print(f"   {status}: {name}")
                if not passed:
                    all_passed = False
            
            return all_passed
        else:
            print(f"❌ Could not get status: {status_response.text}")
            return False


if __name__ == "__main__":
    result = asyncio.run(run_qa_test())
    print("\n" + "=" * 60)
    if result:
        print("🎉 ALL TESTS PASSED!")
    else:
        print("❌ SOME TESTS FAILED!")
    print("=" * 60)
