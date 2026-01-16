import os
from sqlalchemy import  create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. Get the Database URL from the Environment (for Cloud)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./sql_app.db")

# Cleaning: Remove any leading/trailing spaces or quotes that might have been pasted
DATABASE_URL = DATABASE_URL.strip().strip("'").strip('"')

# Handle Heroku/Render 'postgres://' vs SQLAlchemy 'postgresql://'
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# SQLite needs 'check_same_thread: False', Postgres does NOT.
if "sqlite" in DATABASE_URL:
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()