#!/usr/bin/env python3
"""
Migration script to convert conversations from individual message records to JSON arrays.
This script will:
1. Read existing conversations and their messages
2. Convert them to JSON array format
3. Update the database schema
4. Clean up old message records
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, engine
from app.models import Base, Conversation
from sqlalchemy import text
import json
from datetime import datetime

def migrate_conversations():
    """Migrate existing conversations to JSON array format"""
    db = SessionLocal()
    
    try:
        print("🔄 Starting conversation migration...")
        
        # Check if messages table exists (PostgreSQL)
        result = db.execute(text("SELECT table_name FROM information_schema.tables WHERE table_name = 'messages'"))
        messages_table_exists = result.fetchone() is not None
        
        if not messages_table_exists:
            print("ℹ️ Messages table doesn't exist, creating new schema...")
            create_new_schema()
            return
        
        # Get all conversations
        conversations = db.query(Conversation).all()
        print(f"📊 Found {len(conversations)} conversations to migrate")
        
        for conv in conversations:
            print(f"🔄 Migrating conversation {conv.id}...")
            
            # Get all messages for this conversation using raw SQL
            messages_result = db.execute(
                text("SELECT role, content, created_at FROM messages WHERE conversation_id = :conv_id ORDER BY created_at"),
                {"conv_id": conv.id}
            )
            messages = messages_result.fetchall()
            
            if messages:
                # Convert to JSON array format
                messages_array = []
                for msg in messages:
                    messages_array.append({
                        "role": msg.role,
                        "content": msg.content,
                        "timestamp": msg.created_at.isoformat() if msg.created_at else datetime.utcnow().isoformat()
                    })
                
                # Update conversation with JSON array
                conv.messages = messages_array
                print(f"✅ Converted {len(messages)} messages to JSON array")
            else:
                conv.messages = []
                print("⚠️ No messages found, setting empty array")
        
        # Commit all changes
        db.commit()
        print("✅ All conversations migrated successfully!")
        
        # Now we can drop the messages table
        print("🗑️ Dropping old messages table...")
        db.execute(text("DROP TABLE IF EXISTS messages"))
        db.commit()
        print("✅ Messages table dropped!")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def create_new_schema():
    """Create the new schema with JSON column"""
    print("🏗️ Creating new schema...")
    Base.metadata.create_all(bind=engine)
    print("✅ New schema created!")

if __name__ == "__main__":
    print("🚀 Starting database migration...")
    
    # First, migrate existing data
    migrate_conversations()
    
    # Then create new schema
    create_new_schema()
    
    print("🎉 Migration completed successfully!")
    print("\n📋 Summary:")
    print("- Conversations now store messages as JSON arrays")
    print("- Old messages table has been dropped")
    print("- New schema is ready for use") 