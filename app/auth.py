import hashlib
import jwt
import json
from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException, status
from .models import User
from sqlalchemy.orm import Session

# Secret key for JWT (in production, use a secure secret key)
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def hash_password(password: str) -> str:
    """Hash a password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return hash_password(plain_password) == hashed_password

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[dict]:
    """Verify and decode a JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None

def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """Authenticate a user with email and password"""
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get a user by email"""
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, name: str, email: str, password: str, personality: str = None, 
                totem_animal: str = None, totem_emoji: str = None, totem_title: str = None,
                ocean_scores: dict = None) -> User:
    """Create a new user"""
    # Check if user already exists
    existing_user = get_user_by_email(db, email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash the password
    hashed_password = hash_password(password)
    
    # Convert ocean_scores to JSON string if provided
    ocean_scores_json = json.dumps(ocean_scores) if ocean_scores else None
    
    # Create new user
    db_user = User(
        name=name,
        email=email,
        password_hash=hashed_password,
        personality=personality,
        totem_animal=totem_animal,
        totem_emoji=totem_emoji,
        totem_title=totem_title,
        ocean_scores=ocean_scores_json
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user 