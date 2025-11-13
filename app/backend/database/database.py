from typing import List
from datetime import datetime
import sqlalchemy
from sqlalchemy import Enum as SQEnum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy import Column, Integer, String, Float, Text, DateTime

from config import config


DATABASE_URL = config.connection_string

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
