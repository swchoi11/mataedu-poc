from typing import List
from datetime import datetime

from sqlalchemy import Column, Integer, String, Float, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Enum as SQEnum

from sqlalchemy import create_engine, Column, Integer, String
import sqlalchemy
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from config import config

DATABASE_URL = config.connection_string

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
