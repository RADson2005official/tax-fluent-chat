"""Debug models import to find the exact error."""
import sys
import traceback

try:
    print("Importing database...")
    from app.database import Base, engine
    print("✅ Database imported successfully")
    
    print("\nImporting models...")
    from app import models
    print("✅ Models imported successfully")
    
    print("\nCreating tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created successfully!")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\nFull traceback:")
    traceback.print_exc()
