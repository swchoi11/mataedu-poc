from typing import List
from datetime import datetime

from sqlalchemy import Column, Integer, String, Float, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Enum as SQEnum

from sqlalchemy import create_engine, Column, Integer, String
import sqlalchemy
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = config.connection_string

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass



Base.metadata.create_all(bind=engine)

new_item = Item(
    grade = result_1.grade,
    subject = result_1.subject,

    main_chap1 = result_2.main_chap1,
    mid_chap1 = result_2.mid_chap1,
    small_chap1 = result_2.small_chap1,
    reason1 = result_2.reason1,

    main_chap2 = result_2.main_chap2,
    mid_chap2 = result_2.mid_chap2,
    small_chap2 = result_2.small_chap2,
    reason2 = result_2.reason2,

    difficulty = result_3.difficulty,
    difficulty_reason = result_3.difficulty_reason,
    item_type = result_3.item_type,
    points = result_3.points,
    intent = result_3.intent,
    keywords = result_3.keywords,
    content = result_3.content
)

with SessionLocal() as session:
    session.add(new_item)
    session.commit()