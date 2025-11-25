import sys
import os

# Add backend to path
backend_path = os.path.join(os.getcwd(), 'backend')
sys.path.append(backend_path)

try:
    # main.py is in backend/, not backend/app/
    from main import app
    from app.api import ws
    print("Backend imports successful!")
except Exception as e:
    print(f"Backend import failed: {e}")
    import traceback
    traceback.print_exc()
