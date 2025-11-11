from typing import List
from datetime import datetime
from database import Base
from sqlalchemy import Column, Integer, String, Float, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from langchain_core.messages import HumanMessage, SystemMessage, BaseMessage
from typing import List


from langchain.pydantic_v1 import BaseModel, Field


class Problem(Base):
    """개별 문제 테이블"""

    __tablename__ = "problem"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    exam_id: Mapped[int] = mapped_column(Intger, foreign_key=True)
    
    created_time: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now(),
        nullable=False
    )
    grade: Mapped[str] = mapped_column(String, nullable=False)
    subject: Mapped[str] = mapped_column(String)
    main_chap1: Mapped[str] = mapped_column(String)
    mid_chap1: Mapped[str] = mapped_column(String)
    small_chap1: Mapped[str] = mapped_column(String)
    reason1: Mapped[str] = mapped_column(String)
    main_chap2: Mapped[str] = mapped_column(String)
    mid_chap2: Mapped[str] = mapped_column(String)
    small_chap2: Mapped[str] = mapped_column(String)
    reason2: Mapped[str] = mapped_column(String)

    difficulty: Mapped[DiffEnum] = mapped_column(
        SQEnum(DiffEnum),
        nullable=False
    )
    difficulty_reason: Mapped[str] = mapped_column(String, nullable=False)
    item_type: Mapped[ItemTypeEnum] = mapped_column(
        SQEnum(ItemTypeEnum),
        nullable=False
    )
    points: Mapped[int] = mapped_column(Integer)
    intent: Mapped[str] = mapped_column(String)
    keywords: Mapped[str] = mapped_column(String)
    content: Mapped[str] = mapped_column(String)

class Exam(Base):
    """시험지 테이블"""

    __tablename__ = "exam"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    created_time: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utinow,
        nullable=False
    )

class Curriculum(Base):
    __tablename__ = "curriculum"

    id  = Column(Integer, primary_key=True, index=True)
    grade = Column(String, nullable=False)
    subject = Column(String, nullable=False)
    no_main_chapter = Column(Integer, nullable=False)
    main_chapter = Column(String, nullable=False)
    no_sub_chapter = Column(Integer, nullable=True)
    sub_chapter = Column(String, nullable=True)
    no_lesson_chapter = Column(Integer, nullable=True)
    lesson_chapter = Column(String, nullable=True)

class SubjectUnit(Base):
    __tablename__="subject_unit"

    id = Column(Integer, primary_key=True)
    sector = Column(String, nullable=False)
    unit = Column(String, nullable=False)
    unit_exp = Column(String, nullable=False)

