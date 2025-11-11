from typing import List
from datetime import datetime
from database.database import Base
from sqlalchemy import Column, Integer, String, Float, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column


class Problem(Base):
    """개별 문제 테이블"""
    __tablename__ = "problem"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    exam_id: Mapped[int] = mapped_column(Integer)
    
    created_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(), nullable=False)
    grade: Mapped[str] = mapped_column(String, nullable=False)
    subject: Mapped[str] = mapped_column(String, nullable=False)
    
    main_chapter_1: Mapped[str] = mapped_column(String, nullable=False)
    sub_chapter_1: Mapped[str] = mapped_column(String, nullable=False)
    lesson_chapter_1: Mapped[str] = mapped_column(String, nullable=False)
    reason_1: Mapped[str] = mapped_column(String, nullable=False)
    
    main_chapter_2: Mapped[str] = mapped_column(String, nullable=False)
    sub_chapter_2: Mapped[str] = mapped_column(String, nullable=False)
    lesson_chapter_2: Mapped[str] = mapped_column(String, nullable=False)
    reason_2: Mapped[str] = mapped_column(String, nullable=False)
    
    difficulty: Mapped[str] = mapped_column(String, nullable=False)
    difficulty_reason: Mapped[str] = mapped_column(String, nullable=False)
    
    item_type: Mapped[str] = mapped_column(String, nullable=False)
    points: Mapped[int] = mapped_column(Integer, nullable=False)
    
    keywords: Mapped[str] = mapped_column(String, nullable=False)
    content: Mapped[str] = mapped_column(String, nullable=False)
    
    sector_1: Mapped[str] = mapped_column(String, nullable=False)
    unit_1: Mapped[str] = mapped_column(String, nullable=False)
    unit_exp_1: Mapped[str] = mapped_column(String, nullable=False)

    sector_2: Mapped[str] = mapped_column(String, nullable=False)
    unit_2: Mapped[str] = mapped_column(String, nullable=False)
    unit_exp_2: Mapped[str] = mapped_column(String, nullable=False)

    sector_3: Mapped[str] = mapped_column(String, nullable=False)
    unit_3: Mapped[str] = mapped_column(String, nullable=False)
    unit_exp_3: Mapped[str] = mapped_column(String, nullable=False)
  
    
class Exam(Base):
    """시험지 테이블"""

    __tablename__ = "exam"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    created_time: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow(),
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

