# Hashing logic and JWT security
#for jwt token
from jose import jwt
from datetime import datetime, timedelta

import os
SECRET_KEY = os.getenv("SECRET_KEY", "your-default-dev-key-change-this-in-prod")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

import bcrypt

def get_password_hash(password: str):
    # bcrypt 4.0.0+ on Python 3.13 fix:
    # We use the bcrypt library directly because passlib is unmaintained 
    # and has a bug with the 72-character check on newer Python versions.
    pwd_bytes = password.encode('utf-8')
    # Use salt with '2b' (most compatible ident)
    salt = bcrypt.gensalt(rounds=12, prefix=b"2b")
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str):
    try:
        return bcrypt.checkpw(
            plain_password.encode('utf-8'), 
            hashed_password.encode('utf-8')
        )
    except Exception:
        return False

def create_access_token(data:dict):
    to_encode=data.copy()
    expire=datetime.utcnow()+timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp":expire})
    token=jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)
    return token

from jose import JWTError

def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        return username
    except JWTError:
        return None
    