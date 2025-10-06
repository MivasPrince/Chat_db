"""Authentication utilities"""
import os
import hashlib
from dotenv import load_dotenv

load_dotenv()

def hash_password(password: str) -> str:
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def check_authentication(username: str, password: str) -> bool:
    """Check if username and password are valid"""
    correct_username = os.getenv('APP_USERNAME', 'miva_admin')
    correct_password = os.getenv('APP_PASSWORD', 'password')
    
    return username == correct_username and password == correct_password
