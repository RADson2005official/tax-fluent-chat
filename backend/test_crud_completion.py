"""Test script to verify new CRUD operations (Update/Delete) for Dependents, W-2s, and 1099s."""
import sys
import requests
import json
from datetime import datetime

# API base URL
BASE_URL = "http://localhost:8000/api"

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_test(test_name, status, message=""):
    """Print formatted test result."""
    if status:
        print(f"{Colors.OKGREEN}✓{Colors.ENDC} {test_name}")
        if message:
            print(f"  → {message}")
    else:
        print(f"{Colors.FAIL}✗{Colors.ENDC} {test_name}")
        if message:
            print(f"  → {Colors.FAIL}{message}{Colors.ENDC}")

def print_section(title):
    """Print section header."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{title}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")

def get_auth_token():
    """Register/Login to get auth token."""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    test_email = f"test_crud_{timestamp}@example.com"
    test_password = "Test1234"
    
    try:
        # Register
        register_data = {
            "email": test_email,
            "password": test_password,
            "full_name": "Test CRUD User"
        }
        requests.post(f"{BASE_URL}/auth/register", json=register_data, timeout=5)
        
        # Login
        login_data = {
            "username": test_email,
            "password": test_password
        }
        response = requests.post(
            f"{BASE_URL}/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=5
        )
        
        if response.status_code == 200:
            return response.json()['access_token']
        return None
    except Exception as e:
        print(f"Auth failed: {e}")
        return None

def create_tax_form(token):
    """Create a tax form to attach items to."""
    headers = {"Authorization": f"Bearer {token}"}
    form_data = {"year": 2024, "filing_status": "single"}
    response = requests.post(f"{BASE_URL}/tax-forms/", json=form_data, headers=headers)
    if response.status_code == 201:
        return response.json()['id']
    return None

def test_dependent_crud(token, form_id):
    """Test Dependent Update/Delete."""
    print_section("1. Dependent CRUD (Update/Delete)")
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Create
    dep_data = {
        "full_name": "Original Name",
        "ssn": "123-45-6789",
        "date_of_birth": "2015-01-01",
        "relationship": "child",
        "months_lived_with_taxpayer": 12
    }
    res = requests.post(f"{BASE_URL}/tax-forms/{form_id}/dependents", json=dep_data, headers=headers)
    if res.status_code != 201:
        print_test("Create Dependent", False, f"Status: {res.status_code}")
        return
    dep_id = res.json()['id']
    print_test("Create Dependent", True, f"ID: {dep_id}")

    # 2. Update
    update_data = {"full_name": "Updated Name", "relationship": "stepchild"}
    res = requests.put(f"{BASE_URL}/tax-forms/{form_id}/dependents/{dep_id}", json=update_data, headers=headers)
    if res.status_code == 200:
        updated = res.json()
        success = updated['full_name'] == "Updated Name" and updated['relationship'] == "stepchild"
        print_test("Update Dependent", success, f"Name: {updated['full_name']}")
    else:
        print_test("Update Dependent", False, f"Status: {res.status_code}")

    # 3. Delete
    res = requests.delete(f"{BASE_URL}/tax-forms/{form_id}/dependents/{dep_id}", headers=headers)
    if res.status_code == 204:
        print_test("Delete Dependent", True)
        # Verify deletion
        get_res = requests.get(f"{BASE_URL}/tax-forms/{form_id}/dependents", headers=headers)
        dependents = get_res.json()
        found = any(d['id'] == dep_id for d in dependents)
        print_test("Verify Deletion", not found, "Dependent no longer in list")
    else:
        print_test("Delete Dependent", False, f"Status: {res.status_code}")

def test_w2_crud(token, form_id):
    """Test W-2 Update/Delete."""
    print_section("2. W-2 CRUD (Update/Delete)")
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Create
    w2_data = {
        "employer_name": "Original Corp",
        "employer_ein": "12-3456789",
        "box_1_wages": 50000
    }
    res = requests.post(f"{BASE_URL}/tax-forms/{form_id}/w2s", json=w2_data, headers=headers)
    if res.status_code != 201:
        print_test("Create W-2", False, f"Status: {res.status_code}")
        return
    w2_id = res.json()['id']
    print_test("Create W-2", True, f"ID: {w2_id}")

    # 2. Update
    update_data = {"employer_name": "Updated Corp", "box_1_wages": 60000}
    res = requests.put(f"{BASE_URL}/tax-forms/{form_id}/w2s/{w2_id}", json=update_data, headers=headers)
    if res.status_code == 200:
        updated = res.json()
        success = updated['employer_name'] == "Updated Corp" and updated['box_1_wages'] == 60000
        print_test("Update W-2", success, f"Employer: {updated['employer_name']}")
    else:
        print_test("Update W-2", False, f"Status: {res.status_code}")

    # 3. Delete
    res = requests.delete(f"{BASE_URL}/tax-forms/{form_id}/w2s/{w2_id}", headers=headers)
    if res.status_code == 204:
        print_test("Delete W-2", True)
        # Verify
        get_res = requests.get(f"{BASE_URL}/tax-forms/{form_id}/w2s", headers=headers)
        w2s = get_res.json()
        found = any(w['id'] == w2_id for w in w2s)
        print_test("Verify Deletion", not found, "W-2 no longer in list")
    else:
        print_test("Delete W-2", False, f"Status: {res.status_code}")

def test_1099_crud(token, form_id):
    """Test 1099 CRUD (Create/Update/Delete)."""
    print_section("3. 1099 CRUD (Create/Update/Delete)")
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Create
    f1099_data = {
        "form_type": "1099-INT",
        "payer_name": "Bank of Test",
        "payer_ein": "98-7654321",
        "total_amount": 150.50,
        "form_data": {"interest_income": 150.50}
    }
    res = requests.post(f"{BASE_URL}/tax-forms/{form_id}/1099s", json=f1099_data, headers=headers)
    if res.status_code != 201:
        print_test("Create 1099", False, f"Status: {res.status_code}")
        return
    f1099_id = res.json()['id']
    print_test("Create 1099", True, f"ID: {f1099_id}")

    # 2. Update
    update_data = {"payer_name": "Updated Bank", "total_amount": 200.00}
    res = requests.put(f"{BASE_URL}/tax-forms/{form_id}/1099s/{f1099_id}", json=update_data, headers=headers)
    if res.status_code == 200:
        updated = res.json()
        success = updated['payer_name'] == "Updated Bank" and updated['total_amount'] == 200.00
        print_test("Update 1099", success, f"Payer: {updated['payer_name']}")
    else:
        print_test("Update 1099", False, f"Status: {res.status_code}")

    # 3. Delete
    res = requests.delete(f"{BASE_URL}/tax-forms/{form_id}/1099s/{f1099_id}", headers=headers)
    if res.status_code == 204:
        print_test("Delete 1099", True)
        # Verify
        get_res = requests.get(f"{BASE_URL}/tax-forms/{form_id}/1099s", headers=headers)
        f1099s = get_res.json()
        found = any(f['id'] == f1099_id for f in f1099s)
        print_test("Verify Deletion", not found, "1099 no longer in list")
    else:
        print_test("Delete 1099", False, f"Status: {res.status_code}")

def main():
    print(f"\n{Colors.HEADER}{Colors.BOLD}STARTING CRUD COMPLETION TEST{Colors.ENDC}")
    
    # Check health
    try:
        requests.get(f"{BASE_URL}/health", timeout=2)
    except:
        print(f"{Colors.FAIL}Backend not running at {BASE_URL}{Colors.ENDC}")
        sys.exit(1)

    token = get_auth_token()
    if not token:
        print("Failed to get auth token")
        sys.exit(1)
        
    form_id = create_tax_form(token)
    if not form_id:
        print("Failed to create tax form")
        sys.exit(1)
        
    test_dependent_crud(token, form_id)
    test_w2_crud(token, form_id)
    test_1099_crud(token, form_id)
    
    print(f"\n{Colors.OKCYAN}Tests Completed!{Colors.ENDC}\n")

if __name__ == "__main__":
    main()
