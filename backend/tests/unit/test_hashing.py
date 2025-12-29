from app.security import get_password_hash, verify_password

try:
    pwd = "TestPass123!"
    print(f"Hashing password: {pwd}")
    hashed = get_password_hash(pwd)
    print(f"Hashed: {hashed}")
    print(f"Verify: {verify_password(pwd, hashed)}")
except Exception as e:
    print(f"Error: {e}")
