import sys
import os
import requests
from sqlalchemy import create_engine, update
from sqlalchemy.orm import sessionmaker

# Add parent directory to path to import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models import UserProfile
from app.database import SessionLocal

# Setup DB connection
db = SessionLocal()

USER_ID = 1
API_URL = f"http://localhost:8000/api/sdui/dashboard/{USER_ID}"

def set_user_mode(mode):
    print(f"\nSetting user mode to: {mode}")
    # Check if profile exists
    profile = db.query(UserProfile).filter(UserProfile.user_id == USER_ID).first()
    if not profile:
        print("Profile not found, creating...")
        profile = UserProfile(user_id=USER_ID, preferred_mode=mode)
        db.add(profile)
    else:
        profile.preferred_mode = mode
    
    db.commit()

def check_layout(expected_layout):
    print(f"Fetching dashboard...")
    try:
        response = requests.get(API_URL)
        response.raise_for_status()
        data = response.json()
        layout = data.get("layout")
        print(f"Got layout: {layout}")
        
        if layout == expected_layout:
            print("VERIFICATION PASSED")
            return True
        else:
            print(f"VERIFICATION FAILED: Expected {expected_layout}, got {layout}")
            return False
    except Exception as e:
        print(f"Error fetching dashboard: {e}")
        return False

def main():
    try:
        print("=== Starting SDUI Layout Verification ===")
        
        # Test Novice Mode
        set_user_mode("novice")
        if not check_layout("single-column"):
            sys.exit(1)

        # Test Expert Mode
        set_user_mode("expert")
        if not check_layout("bento-grid"):
            sys.exit(1)
            
        print("\n=== All Verifications Passed ===")

    finally:
        db.close()

if __name__ == "__main__":
    main()
