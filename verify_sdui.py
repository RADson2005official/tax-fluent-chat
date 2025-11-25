import requests
import json

try:
    response = requests.get('http://localhost:8000/api/sdui/dashboard/user123')
    response.raise_for_status()
    with open('sdui_response.json', 'w', encoding='utf-8') as f:
        f.write(response.text)
    print("SDUI Verification: SUCCESS")
except Exception as e:
    print(f"SDUI Verification: FAILED - {e}")
