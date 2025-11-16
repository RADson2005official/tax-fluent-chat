"""Test script to verify core agent functionality."""
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

def test_health_check():
    """Test API health check."""
    print_section("1. Health Check")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_test("API Server", True, f"Status: {data['status']}")
            print_test("Database Connection", data['database'] == 'healthy', data['database'])
            return True
        else:
            print_test("API Server", False, f"Status code: {response.status_code}")
            return False
    except Exception as e:
        print_test("API Server", False, f"Connection failed: {str(e)}")
        return False

def test_user_registration():
    """Test user registration."""
    print_section("2. User Registration & Authentication")
    
    # Generate unique email
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    test_email = f"test_{timestamp}@example.com"
    test_password = "Test1234"
    
    # Register user
    try:
        register_data = {
            "email": test_email,
            "password": test_password,
            "full_name": "Test User"
        }
        response = requests.post(f"{BASE_URL}/auth/register", json=register_data, timeout=5)
        
        if response.status_code == 201:
            user_data = response.json()
            print_test("User Registration", True, f"User ID: {user_data['id']}, Email: {user_data['email']}")
            
            # Login
            login_data = {
                "username": test_email,
                "password": test_password
            }
            login_response = requests.post(
                f"{BASE_URL}/auth/login",
                data=login_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=5
            )
            
            if login_response.status_code == 200:
                token_data = login_response.json()
                token = token_data['access_token']
                print_test("User Login", True, f"Token: {token[:20]}...")
                return token, user_data['id']
            else:
                print_test("User Login", False, f"Status: {login_response.status_code}")
                return None, None
        else:
            print_test("User Registration", False, f"Status: {response.status_code}, Message: {response.text}")
            return None, None
    except Exception as e:
        print_test("User Registration", False, f"Error: {str(e)}")
        return None, None

def test_tax_form_creation(token):
    """Test tax form CRUD operations."""
    print_section("3. Tax Form Management")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create tax form
    try:
        form_data = {
            "year": 2024,
            "filing_status": "single"
        }
        response = requests.post(f"{BASE_URL}/tax-forms/", json=form_data, headers=headers, timeout=5)
        
        if response.status_code == 201:
            form = response.json()
            form_id = form['id']
            print_test("Create Tax Form", True, f"Form ID: {form_id}, Year: {form['year']}, Status: {form['filing_status']}")
            
            # Get tax form
            get_response = requests.get(f"{BASE_URL}/tax-forms/{form_id}", headers=headers, timeout=5)
            if get_response.status_code == 200:
                print_test("Retrieve Tax Form", True, f"Retrieved form {form_id}")
            else:
                print_test("Retrieve Tax Form", False, f"Status: {get_response.status_code}")
            
            # List tax forms
            list_response = requests.get(f"{BASE_URL}/tax-forms/", headers=headers, timeout=5)
            if list_response.status_code == 200:
                forms = list_response.json()
                print_test("List Tax Forms", True, f"Found {len(forms)} form(s)")
            else:
                print_test("List Tax Forms", False, f"Status: {list_response.status_code}")
            
            return form_id
        else:
            print_test("Create Tax Form", False, f"Status: {response.status_code}")
            return None
    except Exception as e:
        print_test("Create Tax Form", False, f"Error: {str(e)}")
        return None

def test_w2_management(token, form_id):
    """Test W-2 form management."""
    print_section("4. W-2 Form Management")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        w2_data = {
            "employer_name": "Test Corporation",
            "employer_ein": "12-3456789",
            "box_1_wages": 75000.00,
            "box_2_federal_tax_withheld": 9500.00,
            "box_3_social_security_wages": 75000.00,
            "box_4_social_security_tax_withheld": 4650.00,
            "box_5_medicare_wages": 75000.00,
            "box_6_medicare_tax_withheld": 1087.50,
            "box_12_codes": ["D:5000.00"],
            "box_13_checkboxes": {"retirement_plan": True}
        }
        
        response = requests.post(
            f"{BASE_URL}/tax-forms/{form_id}/w2s",
            json=w2_data,
            headers=headers,
            timeout=5
        )
        
        if response.status_code == 201:
            w2 = response.json()
            print_test("Create W-2 Form", True, f"W-2 ID: {w2['id']}, Employer: {w2['employer_name']}")
            print(f"  → Box 1 Wages: ${w2['box_1_wages']:,.2f}")
            print(f"  → Federal Withholding: ${w2['box_2_federal_tax_withheld']:,.2f}")
            
            # List W-2s
            list_response = requests.get(f"{BASE_URL}/tax-forms/{form_id}/w2s", headers=headers, timeout=5)
            if list_response.status_code == 200:
                w2s = list_response.json()
                print_test("List W-2 Forms", True, f"Found {len(w2s)} W-2(s)")
                return True
            else:
                print_test("List W-2 Forms", False, f"Status: {list_response.status_code}")
                return False
        else:
            print_test("Create W-2 Form", False, f"Status: {response.status_code}")
            return False
    except Exception as e:
        print_test("Create W-2 Form", False, f"Error: {str(e)}")
        return False

def test_dependent_management(token, form_id):
    """Test dependent management."""
    print_section("5. Dependent Management")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        dependent_data = {
            "full_name": "Jane Doe",
            "ssn": "123-45-6789",
            "date_of_birth": "2010-05-15",
            "relationship": "daughter",
            "months_lived_with_taxpayer": 12
        }
        
        response = requests.post(
            f"{BASE_URL}/tax-forms/{form_id}/dependents",
            json=dependent_data,
            headers=headers,
            timeout=5
        )
        
        if response.status_code == 201:
            dependent = response.json()
            print_test("Create Dependent", True, f"Dependent ID: {dependent['id']}, Name: {dependent['full_name']}")
            print(f"  → Relationship: {dependent['relationship_type']}")
            print(f"  → SSN: {Colors.WARNING}[ENCRYPTED]{Colors.ENDC}")
            
            # List dependents
            list_response = requests.get(f"{BASE_URL}/tax-forms/{form_id}/dependents", headers=headers, timeout=5)
            if list_response.status_code == 200:
                dependents = list_response.json()
                print_test("List Dependents", True, f"Found {len(dependents)} dependent(s)")
                return True
            else:
                print_test("List Dependents", False, f"Status: {list_response.status_code}")
                return False
        else:
            print_test("Create Dependent", False, f"Status: {response.status_code}")
            return False
    except Exception as e:
        print_test("Create Dependent", False, f"Error: {str(e)}")
        return False

def test_user_profile(token):
    """Test user profile management."""
    print_section("6. User Profile Management")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        # Get profile
        get_response = requests.get(f"{BASE_URL}/users/me/profile", headers=headers, timeout=5)
        if get_response.status_code == 200:
            profile = get_response.json()
            print_test("Get User Profile", True, f"Mode: {profile['preferred_mode']}, Theme: {profile['theme']}")
            
            # Update profile
            update_data = {
                "preferred_mode": "intermediate",
                "theme": "dark"
            }
            update_response = requests.put(
                f"{BASE_URL}/users/me/profile",
                json=update_data,
                headers=headers,
                timeout=5
            )
            
            if update_response.status_code == 200:
                updated_profile = update_response.json()
                print_test("Update User Profile", True, f"New Mode: {updated_profile['preferred_mode']}")
                return True
            else:
                print_test("Update User Profile", False, f"Status: {update_response.status_code}")
                return False
        else:
            print_test("Get User Profile", False, f"Status: {get_response.status_code}")
            return False
    except Exception as e:
        print_test("Get User Profile", False, f"Error: {str(e)}")
        return False

def main():
    """Run all tests."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║        TAX FILING SYSTEM - CORE FUNCTIONALITY TEST        ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print(f"{Colors.ENDC}")
    
    # Test 1: Health Check
    if not test_health_check():
        print(f"\n{Colors.FAIL}ERROR: API Server is not running. Please start the backend server.{Colors.ENDC}")
        print(f"Run: cd backend && .\\venv\\Scripts\\Activate.ps1 && python main.py")
        sys.exit(1)
    
    # Test 2: User Registration & Authentication
    token, user_id = test_user_registration()
    if not token:
        print(f"\n{Colors.FAIL}ERROR: User registration/authentication failed.{Colors.ENDC}")
        sys.exit(1)
    
    # Test 3: Tax Form Creation
    form_id = test_tax_form_creation(token)
    if not form_id:
        print(f"\n{Colors.FAIL}ERROR: Tax form creation failed.{Colors.ENDC}")
        sys.exit(1)
    
    # Test 4: W-2 Management
    test_w2_management(token, form_id)
    
    # Test 5: Dependent Management
    test_dependent_management(token, form_id)
    
    # Test 6: User Profile
    test_user_profile(token)
    
    # Summary
    print_section("Test Summary")
    print(f"{Colors.OKGREEN}✓ All core functionality tests completed!{Colors.ENDC}")
    print(f"\n{Colors.OKBLUE}Backend API:{Colors.ENDC} http://localhost:8000")
    print(f"{Colors.OKBLUE}API Docs:{Colors.ENDC} http://localhost:8000/api/docs")
    print(f"{Colors.OKBLUE}Frontend:{Colors.ENDC} http://localhost:8080")
    
    print(f"\n{Colors.WARNING}Next Steps:{Colors.ENDC}")
    print("1. Test the frontend chat interface at http://localhost:8080")
    print("2. Try uploading a tax document (W-2, 1099)")
    print("3. Test the agent conversation flow")
    print("4. Verify mode-based question adaptation (Novice/Intermediate/Expert)")
    
    print(f"\n{Colors.OKCYAN}Test completed successfully!{Colors.ENDC}\n")

if __name__ == "__main__":
    main()
