"""Test database connection and setup."""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '.env.dev'))

def test_database_connection():
    """Test database connection and display information."""
    print("=" * 60)
    print("🔍 Testing Database Connection")
    print("=" * 60)
    
    # Get database URL
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL not found in environment variables")
        return False
    
    print(f"\n📍 Database URL: {database_url.split('@')[1] if '@' in database_url else 'N/A'}")
    
    try:
        # Create engine
        print("\n⏳ Creating database engine...")
        engine = create_engine(database_url, pool_pre_ping=True)
        
        # Test connection
        print("⏳ Testing connection...")
        with engine.connect() as connection:
            result = connection.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            
            print("\n✅ Database connection successful!")
            print(f"📊 PostgreSQL Version: {version}")
            
            # Test schema
            result = connection.execute(text("""
                SELECT schema_name 
                FROM information_schema.schemata 
                WHERE schema_name IN ('public', 'tax_data');
            """))
            schemas = [row[0] for row in result.fetchall()]
            print(f"📂 Available schemas: {', '.join(schemas)}")
            
            # Test extensions
            result = connection.execute(text("""
                SELECT extname 
                FROM pg_extension 
                WHERE extname IN ('uuid-ossp', 'pgcrypto');
            """))
            extensions = [row[0] for row in result.fetchall()]
            print(f"🔧 Installed extensions: {', '.join(extensions) if extensions else 'None yet'}")
            
            print("\n" + "=" * 60)
            print("✅ All database checks passed!")
            print("=" * 60)
            
            return True
            
    except Exception as e:
        print(f"\n❌ Database connection failed:")
        print(f"   Error: {str(e)}")
        print("\n💡 Troubleshooting:")
        print("   1. Verify PostgreSQL is running")
        print("   2. Check DATABASE_URL in .env.dev")
        print("   3. Verify credentials and database exists")
        print("   4. Check firewall settings")
        return False


def create_tables():
    """Create database tables."""
    print("\n" + "=" * 60)
    print("📋 Creating Database Tables")
    print("=" * 60)
    
    try:
        from app.database import engine, Base
        from app import models  # Import models to register them
        
        print("\n⏳ Creating all tables...")
        Base.metadata.create_all(bind=engine)
        
        print("✅ All tables created successfully!")
        
        # List created tables
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        print(f"\n📊 Created tables ({len(tables)}):")
        for table in sorted(tables):
            print(f"   • {table}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Failed to create tables:")
        print(f"   Error: {str(e)}")
        return False


if __name__ == "__main__":
    print("\n🚀 Tax Filing AI Agent - Database Setup\n")
    
    # Test connection
    if test_database_connection():
        # Create tables
        create_tables()
        
        print("\n" + "=" * 60)
        print("🎉 Database setup complete!")
        print("=" * 60)
        print("\nNext steps:")
        print("  1. Start the FastAPI backend:")
        print("     uvicorn app.main:app --reload")
        print("  2. Access API documentation:")
        print("     http://localhost:8000/docs")
        print("\n")
    else:
        print("\n⚠️  Please fix database connection issues before proceeding.")
        print("📖 See POSTGRESQL_SETUP.md for detailed setup instructions.\n")
        sys.exit(1)
