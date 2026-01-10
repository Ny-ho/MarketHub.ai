from sqlalchemy import Column, Integer, String
from database import Base

class JobDB(Base):
    __tablename__ = "jobs" # This will be the table name in SQL

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    location = Column(String)
    salary = Column(Integer)

class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)