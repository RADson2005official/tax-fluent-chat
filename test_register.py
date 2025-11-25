import requests
import json

url = "http://localhost:8000/api/auth/register"
payload = {
    "email": "test_script@example.com",
    "password": "TestPass123!",
    "full_name": "Test Script User"
}
headers = {
    "Content-Type": "application/json"
}

try:
    response = requests.post(url, json=payload, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
