from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class SuggestedCurriculum(BaseModel):
    main_chapter: str
    sub_chapter: str
    lesson_chapter: str
    reason: str

class Intent(BaseModel):
    sector: str
    criteria: str
    criteria_explanation: str

class Difficulty(BaseModel):
    difficulty: str
    difficulty_reason: str

class ProblemMetadata(BaseModel):
    grade: str
    subject: str
    suggested_curriculum_1: SuggestedCurriculum
    suggested_curriculum_2: Optional[SuggestedCurriculum] = None
    intent_1: Intent
    intent_2: Optional[Intent] = None
    intent_3: Optional[Intent] = None
    difficulty: Difficulty
    item_type: str
    points: int
    keywords: str
    content: str

class ProblemAnalysisResponse(BaseModel):
    problem_id: str
    metadata: ProblemMetadata

    @classmethod
    def from_analysis(cls, problem_id: str, analysis: Dict[str, Any]) -> "ProblemAnalysisResponse":
        """
        분석 결과 딕셔너리에서 ProblemAnalysisResponse 객체를 생성합니다.
        """
        metadata = ProblemMetadata(
            grade=analysis["inferenced_grade"].grade,
            subject=analysis["inferenced_grade"].subject,
            suggested_curriculum_1=SuggestedCurriculum(
                main_chapter=analysis["unit_suggestions"].main_chapter_1,
                sub_chapter=analysis["unit_suggestions"].sub_chapter_1,
                lesson_chapter=analysis["unit_suggestions"].lesson_chapter_1,
                reason=analysis["unit_suggestions"].reason_1,
            ),
            suggested_curriculum_2=SuggestedCurriculum(
                main_chapter=analysis["unit_suggestions"].main_chapter_2,
                sub_chapter=analysis["unit_suggestions"].sub_chapter_2,
                lesson_chapter=analysis["unit_suggestions"].lesson_chapter_2,
                reason=analysis["unit_suggestions"].reason_2,
            ) if analysis["unit_suggestions"].main_chapter_2 else None,
            intent_1=Intent(
                sector=analysis["intent_criterias"].sector_1,
                criteria=analysis["intent_criterias"].criteria_1,
                criteria_explanation=analysis["intent_criterias"].criteria_explanation_1,
            ),
            intent_2=Intent(
                sector=analysis["intent_criterias"].sector_2,
                criteria=analysis["intent_criterias"].criteria_2,
                criteria_explanation=analysis["intent_criterias"].criteria_explanation_2,
            ) if analysis["intent_criterias"].sector_2 else None,
            intent_3=Intent(
                sector=analysis["intent_criterias"].sector_3,
                criteria=analysis["intent_criterias"].criteria_3,
                criteria_explanation=analysis["intent_criterias"].criteria_explanation_3,
            ) if analysis["intent_criterias"].sector_3 else None,
            difficulty=Difficulty(
                difficulty=analysis["metadata"].difficulty,
                difficulty_reason=analysis["metadata"].difficulty_reason,
            ),
            item_type=analysis["metadata"].item_type,
            points=analysis["metadata"].points,
            keywords=analysis["metadata"].keywords,
            content=analysis["metadata"].content,
        )
        return cls(problem_id=problem_id, metadata=metadata)


class ExamAnalysisResponse(BaseModel):
    exam_id: str
    status: str