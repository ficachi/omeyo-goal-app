#!/usr/bin/env python3
"""
Script to export totem personalities data to Supabase
"""
import os
import sys
from pathlib import Path

# Add the app directory to the path
sys.path.append(str(Path(__file__).parent / "app"))

from supabase_config import get_supabase_client

def export_totem_personalities():
    """Export totem personalities data to Supabase"""
    try:
        # Get Supabase client
        supabase = get_supabase_client()
        
        print("🔗 Connecting to Supabase...")
        
        # Read the SQL file
        sql_file_path = Path(__file__).parent / "export_totem_personalities.sql"
        with open(sql_file_path, 'r', encoding='utf-8') as file:
            sql_content = file.read()
        
        print("📝 Executing SQL to create table and insert data...")
        
        # Execute the SQL
        result = supabase.rpc('exec_sql', {'sql': sql_content}).execute()
        
        print("✅ Successfully exported totem personalities to Supabase!")
        print(f"📊 Table 'totem_personalities' created with all 20 animal totem personalities")
        
        # Verify the data was inserted
        print("\n🔍 Verifying data...")
        response = supabase.table('totem_personalities').select('*').execute()
        
        if response.data:
            print(f"✅ Found {len(response.data)} totem personalities in the database")
            print("\n📋 Sample entries:")
            for i, personality in enumerate(response.data[:3]):
                print(f"  {i+1}. {personality['title']} ({personality['animal']} {personality['emoji']})")
                print(f"     High: {personality['high_trait']}, Low: {personality['low_trait']}")
        else:
            print("⚠️  No data found in the table")
            
    except Exception as e:
        print(f"❌ Error exporting to Supabase: {e}")
        print("\n💡 Alternative: You can manually execute the SQL in your Supabase dashboard:")
        print("1. Go to your Supabase project dashboard")
        print("2. Navigate to SQL Editor")
        print("3. Copy and paste the contents of 'export_totem_personalities.sql'")
        print("4. Execute the SQL")

def manual_export_instructions():
    """Print manual export instructions"""
    print("\n📋 MANUAL EXPORT INSTRUCTIONS:")
    print("=" * 50)
    print("1. Go to your Supabase project dashboard")
    print("2. Navigate to 'SQL Editor' in the left sidebar")
    print("3. Create a new query")
    print("4. Copy the contents of 'export_totem_personalities.sql'")
    print("5. Paste it into the SQL editor")
    print("6. Click 'Run' to execute")
    print("7. Verify the table was created in 'Table Editor'")
    print("\n📁 SQL file location: backend/export_totem_personalities.sql")

if __name__ == "__main__":
    print("🦁 Exporting Animal Totem Personalities to Supabase")
    print("=" * 60)
    
    # Check if Supabase is configured
    if not os.getenv("SUPABASE_URL") or not os.getenv("SUPABASE_SERVICE_ROLE_KEY"):
        print("❌ Supabase not configured. Please set up your environment variables:")
        print("   - SUPABASE_URL")
        print("   - SUPABASE_SERVICE_ROLE_KEY")
        print("   - SUPABASE_ANON_KEY")
        manual_export_instructions()
    else:
        try:
            export_totem_personalities()
        except Exception as e:
            print(f"❌ Automated export failed: {e}")
            manual_export_instructions() 