from typing import Optional
from dataclasses import dataclass

@dataclass
class ExamProcessRequest:
    file_path: str
    title: str
    description: str

@dataclass
class ExamProcessResponse:
    file_id: str
    status: str

@dataclass
class ExamAnalysisResponse:
    file_id: str
    analysis_report: dict

@dataclass
class ItemAnalysisRequest:
    item_file_path: str
    query: Optional[str] = None

@dataclass
class ItemAnalysisRepsonse:
    item_id: str
    metadata: dict

from langchain.pydantic_v1 import BaseModel, Field
from enum import Enum

class Curriculum(BaseModel):
    """커리큘럼 정보 모델"""
    grade: str = Field(description="학년")
    subject: str = Field(description="과목")
    main_chap: str = Field(description="대단원")
    mid_chap: str = Field(description="중단원")
    small_chap: str = Field(description="소단원")


class Suggestions(BaseModel):
    """단원 제안 모델"""
    main_chap1: str = Field(description="첫번째 추천 대단원")
    mid_chap1: str = Field(description="첫번째 추천 중단원")
    small_chap1: str = Field(description="첫번째 추천 소단원")
    reason1: str = Field(description="첫번째 추천 이유")
    main_chap2: Optional[str] = Field(description="두번째 추천 대단원")
    mid_chap2: Optional[str] = Field(description="두번째 추천 중단원")
    small_chap2: Optional[str] = Field(description="두번째 추천 소단원")
    reason2: Optional[str] = Field(description="두번째 추천 이유")



class DiffEnum(str, Enum):
    EASY="하"
    INTERMEDIATE="중"
    HARD ="상"

class ItemTypeEnum(str, Enum):
    MULTIPLE_CHOICE="5지선다"
    COMPLEX_CHOICE="조합형"
    SHORT_ANSWER="단답형"
    ESSAY_ANSWER="서술형"

class Metadata(BaseModel):
    difficulty: DiffEnum = Field(description="난이도 (예: 상, 중, 하)")
    difficulty_reason: str = Field(description="난이도 평가 이유")
    item_type: ItemTypeEnum = Field(description="문제 유형 (예: 5지선다, 조합형, 단답형, 서술형)")
    points: int = Field(description="배점")
    intent: str = Field(description="출제의도")
    keywords: str = Field(description="핵심 키워드 (예: '삼각함수, 로그')")
    content: str = Field(description="파일에서 인식된 문제 텍스트 전체")
