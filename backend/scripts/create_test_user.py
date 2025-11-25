import sys
import os

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.database import SessionLocal
from app import crud, schemas, models

def create_test_user():
    db = SessionLocal()
    try:
        email = "testuser@example.com"
        existing_user = crud.get_user_by_email(db, email)
        if existing_user:
            print(f"User {email} already exists with ID: {existing_user.id}")
            return existing_user.id
        
        user_in = schemas.UserCreate(
            email=email,
            password="Password123!",
            full_name="Test User"
        )
        user = crud.create_user(db, user_in)
        print(f"Created user {email} with ID: {user.id}")
        return user.id
    except Exception as e:
        print(f"Error creating user: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_test_user()
