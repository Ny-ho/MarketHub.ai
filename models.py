from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class UserDB(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email=Column(String,unique=True,index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    
    # This creates a virtual link to Todos
    todos = relationship("TodoDB", back_populates="owner")

class TodoDB(Base):
    __tablename__ = "todos"
    id = Column(Integer, primary_key=True, index=True)
    task = Column(String)
    is_done = Column(Boolean, default=False)
    
    # This is the "ID badge" saying which user owns this task
    owner_id = Column(Integer, ForeignKey("users.id"))
    
    # This creates a virtual link back to the User
    owner = relationship("UserDB", back_populates="todos")

class JobDB(Base):
    __tablename__ = "jobs"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    location = Column(String)
    salary = Column(Integer)
    description = Column(String, nullable=True)
