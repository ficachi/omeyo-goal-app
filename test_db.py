import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from app.models import Base

# Load environment variables
load_dotenv()

def test_database_connection():
    """Test the database connection and create tables"""
    
    # Get database URL from environment
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        print("❌ DATABASE_URL not found in environment variables!")
        print("Please add DATABASE_URL to your .env file")
        print("Example: DATABASE_URL=postgresql://postgres:password@db.project.supabase.co:5432/postgres")
        return False
    
    try:
        # Create engine
        print(f"🔗 Connecting to database...")
        engine = create_engine(database_url)
        
        # Test connection
        with engine.connect() as connection:
            result = connection.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            print(f"✅ Connected successfully!")
            print(f"📊 Database version: {version}")
        
        # Create tables
        print("🏗️  Creating tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ Tables created successfully!")
        
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("\n🔧 Troubleshooting tips:")
        print("1. Check your DATABASE_URL in .env file")
        print("2. Make sure your Supabase project is active")
        print("3. Verify your password is correct")
        print("4. Check if your IP is allowed in Supabase settings")
        return False

if __name__ == "__main__":
    test_database_connection() 