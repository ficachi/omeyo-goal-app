#!/usr/bin/env python3
"""
Script to check footprints data and database schema
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models import Footprint
from sqlalchemy import text

def check_footprints():
    db = SessionLocal()
    try:
        print("🔍 Checking footprints for user 1...")
        
        # Check if footprints table exists and has data
        result = db.execute(text("SELECT COUNT(*) FROM footprints WHERE user_id = 1"))
        count = result.scalar()
        print(f"📊 Found {count} footprints for user 1")
        
        if count > 0:
            # Get all footprints for user 1
            footprints = db.query(Footprint).filter(Footprint.user_id == 1).all()
            print("\n📋 Footprints for user 1:")
            for fp in footprints:
                print(f"  - ID: {fp.id}, Action: {fp.action}, Due: {fp.due_time}, Completed: {fp.is_completed}")
        
        # Check database schema
        print("\n🏗️ Checking database schema...")
        result = db.execute(text("""
            SELECT column_name, data_type, is_nullable 
            FROM information_schema.columns 
            WHERE table_name = 'footprints' 
            ORDER BY ordinal_position
        """))
        
        print("📋 Footprints table schema:")
        for row in result:
            print(f"  - {row[0]}: {row[1]} (nullable: {row[2]})")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    check_footprints() 