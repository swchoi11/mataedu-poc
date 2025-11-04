from typing import List
from database import Base
from datetime import datetime

from sqlalchemy import Column, Integer, String, Float, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column


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

class Item(Base):
    """개별 문제 테이블"""

    __tablename__ = "item"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    created_time: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now(),
        nullable=False
    )


class Curriculum(Base):
    __tablename__ = "curriculum"

    id  = Column(Integer, primary_key=True, index=True)
    grade = Column(String, nullable=False)
    subject = Column(String, nullable=False)
    main_chap_num = Column(Integer, nullable=False, index=True)
    main_chap = Column(String, nullable=False, unique=True)
    mid_chap_num = Column(Integer, nullable=True)
    mid_chap = Column(String, nullable=True)
    small_chap_num = Column(Integer, nullable=True)
    small_chap = Column(String, nullable=True)

class ItemMeta(Base):
    __tablename__ = "item_meta"

    id = Column(Integer, primary_key=True, index=True)
    curriculum_id = Column(Integer)
    difficulty = Column(String)
    intent = Column(Text)
    item_type = Column(String)
    points = Column(Integer)
    
