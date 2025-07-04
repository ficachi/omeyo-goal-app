from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
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
    action = Column(String)
    path_name = Column(String)
    path_color = Column(String)
    due_time = Column(String)
    is_completed = Column(Integer, default=0)  # 0 = False, 1 = True
    priority = Column(Integer)
    user = relationship("User", backref="footprints")

def create_tables():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    print("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    print("Creating all tables...")
    Base.metadata.create_all(bind=engine)
    print("Done.") 