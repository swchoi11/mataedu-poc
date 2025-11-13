from langchain.pydantic_v1 import BaseModel, Field
from typing import List, Optional
from enum import Enum

class Curriculum(BaseModel):
    """커리큘럼 정보 모델"""
    grade: str = Field(description="학년")
    subject: str = Field(description="과목")
    no_main_chapter: int = Field(description="대단원 번호")
    main_chapter: str = Field(description="대단원")
    no_sub_chapter: int = Field(description="중단원 번호")
    sub_chapter: str = Field(description="중단원")
    no_lesson_chapter: int = Field(description="소단원 번호")
    lesson_chapter: str = Field(description="소단원")
    
class UnitSuggestions(BaseModel):
    """교과 단원 추천 모델"""
    main_chapter_1: str = Field(description="첫번째 추천 대단원")
    sub_chapter_1: str = Field(description="첫번째 추천 중단원")
    lesson_chapter_1: str = Field(description="첫번째 추천 소단원")
    reason_1: str = Field(description="첫번째 추천 이유")
    main_chapter_2: Optional[str] = Field(description="두번째 추천 대단원")
    sub_chapter_2: Optional[str] = Field(description="두번째 추천 중단원")
    lesson_chapter_2: Optional[str] = Field(description="두번째 추천 소단원")
    reason_2: Optional[str] = Field(description="두번째 추천 이유")
    
class IntentSuggestions(BaseModel):
    """출제 의도 추천 모델"""
    sector_1: str = Field(description="수행과정1")
    criteria_1: str = Field(description="수행과정1에서 학생이 취득해야하는 성취 기준")
    criteria_explanation_1: str = Field(description="성취 기준1에 대한 구체적 설명")
    sector_2: Optional[str] = Field(description="수행과정2")
    criteria_2: Optional[str] = Field(description="수행과정2에서 학생이 취득해야하는 성취 기준")
    criteria_explanation_2: Optional[str] = Field(description="성취 기준2에 대한 구체적 설명")
    sector_3: Optional[str] = Field(description="수행과정3")
    criteria_3: Optional[str] = Field(description="수행과정3에서 학생이 취득해야하는 성취 기준")
    criteria_explanation_3: Optional[str] = Field(description="성취 기준3에 대한 구체적 설명")

class DiffEnum(str, Enum):
    EASY="하"
    INTERMEDIATE="중"
    HARD ="상"

class ItemTypeEnum(str, Enum):
    MULTIPLE_CHOICE="5지선다"
    COMPLEX_CHOICE="조합형"
    SHORT_ANSWER="단답형"
    ESSAY_ANSWER="서술형"

class MetadataSuggestion(BaseModel):
    difficulty: DiffEnum = Field(description="난이도 (예: 상, 중, 하)")
    difficulty_reason: str = Field(description="난이도 평가 이유")
    item_type: ItemTypeEnum = Field(description="문제 유형 (예: 5지선다, 조합형, 단답형, 서술형)")
    points: int = Field(description="배점")
    keywords: str = Field(description="핵심 키워드 (예: '삼각함수, 로그')")
    content: str = Field(description="파일에서 인식된 문제 텍스트 전체")

from pydantic import BaseModel as PydanticV2BaseModel, Field as PydanticV2Field, model_validator

class QuestionBox(PydanticV2BaseModel):
    """
    개별 문항의 정보와 위치를 담는 스키마.
    좌표는 (0.0 ~ 1.0) 사이의 상대 좌표입니다.
    """
    question_number: str = PydanticV2Field(description="문제 번호 (예: '1', '9번', '서술형 2')")
    y_min: float = PydanticV2Field(description="영역의 상단(Top) Y 상대 좌표 (0.0~1.0)")
    x_min: float = PydanticV2Field(description="영역의 좌측(Left) X 상대 좌표 (0.0~1.0)")
    y_max: float = PydanticV2Field(description="영역의 하단(Bottom) Y 상대 좌표 (0.0~1.0)")
    x_max: float = PydanticV2Field(description="영역의 우측(Right) X 상대 좌표 (0.0~1.0)")

class QuestionList(PydanticV2BaseModel):
    questions: List[QuestionBox] = PydanticV2Field(description = "페이지에서 감지된 모든 개별 문항의 리스트")

    @model_validator(mode='before')
    @classmethod
    def wrap_list_in_dict(cls, values):
        """
        llm이 리스트를 반환한 경우 딕셔너리로 변환
        """
        if isinstance(values, list):
            return {"questions": values}
        return values
