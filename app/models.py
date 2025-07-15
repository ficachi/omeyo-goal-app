from sqlalchemy import Column, Integer, String, ForeignKey, Date, Boolean, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import engine

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    personality = Column(String)
    totem_animal = Column(String)
    totem_emoji = Column(String)
    totem_title = Column(String)
    ocean_scores = Column(String)  # JSON string of personality scores
    goals = relationship("Goal", back_populates="user")
    paths = relationship("Path", back_populates="user")
    conversations = relationship("Conversation", back_populates="user")

class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String, default="New Conversation")
    personality = Column(String, default="coach")
    messages = Column(JSON)  # Store messages as JSON array
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user = relationship("User", back_populates="conversations")

class Path(Base):
    __tablename__ = "paths"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String, index=True)
    color = Column(String, default="bg-purple-100 text-purple-800")
    is_active = Column(Boolean, default=True)
    is_completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="paths")
    footprints = relationship("Footprint", back_populates="path")

class Goal(Base):
    __tablename__ = "goals"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    description = Column(String)
    status = Column(String)
    user = relationship("User", back_populates="goals")

class Footprint(Base):
    __tablename__ = "footprints"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    path_id = Column(Integer, ForeignKey("paths.id"), nullable=True)
    action = Column(String)
    path_name = Column(String)
    path_color = Column(String)
    due_time = Column(Date)
    is_completed = Column(Integer, default=0)  # 0 = False, 1 = True
    priority = Column(Integer)
    user = relationship("User", backref="footprints")
    path = relationship("Path", back_populates="footprints")

def create_tables():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    print("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    print("Creating all tables...")
    Base.metadata.create_all(bind=engine)
    print("Done.") 