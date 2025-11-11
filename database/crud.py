from sqlalchemy.orm import Session
from typing import Optional
from database.entities import Problem
from custom_langchain.models import Curriculum, UnitSuggestions, IntentSuggestions, MetadataSuggestion


def save_problem_analysis(
    db: Session,
    exam_id: int,
    analysis: dict
) -> int:
    """
    랭체인 분석 결과를 데이터베이스에 저장

    Args:
        db: 데이터베이스 세션
        exam_id: 시험지 ID
        analysis: 랭체인 분석 결과 딕셔너리

    Returns:
        저장된 문제의 ID
    """
    curriculum: Curriculum = analysis["curriculum"]
    suggestions: UnitSuggestions = analysis["unit_suggestions"]
    criterias: IntentSuggestions = analysis["intent_criterias"]
    metadata: Optional[MetadataSuggestion] = analysis.get("metadata")

    # Problem 엔티티 생성
    problem = Problem(
        exam_id=exam_id,

        # 커리큘럼 정보
        grade=curriculum.grade,
        subject=curriculum.subject,

        # 교과 단원 추천 1
        main_chapter_1=suggestions.main_chapter_1,
        sub_chapter_1=suggestions.sub_chapter_1,
        lesson_chapter_1=suggestions.lesson_chapter_1,
        reason_1=suggestions.reason_1,

        # 교과 단원 추천 2 (Optional)
        main_chapter_2=suggestions.main_chapter_2 or "",
        sub_chapter_2=suggestions.sub_chapter_2 or "",
        lesson_chapter_2=suggestions.lesson_chapter_2 or "",
        reason_2=suggestions.reason_2 or "",

        # 메타데이터 (metadata가 없으면 기본값)
        difficulty=metadata.difficulty if metadata else "중",
        difficulty_reason=metadata.difficulty_reason if metadata else "",
        item_type=metadata.item_type if metadata else "5지선다",
        points=metadata.points if metadata else 0,
        keywords=metadata.keywords if metadata else "",
        content=metadata.content if metadata else "",

        # 출제 의도/성취기준 1
        sector_1=criterias.sector_1,
        unit_1=criterias.criteria_1,
        unit_exp_1=criterias.criteria_explanation_1,

        # 출제 의도/성취기준 2 (Optional)
        sector_2=criterias.sector_2 or "",
        unit_2=criterias.criteria_2 or "",
        unit_exp_2=criterias.criteria_explanation_2 or "",

        # 출제 의도/성취기준 3 (Optional)
        sector_3=criterias.sector_3 or "",
        unit_3=criterias.criteria_3 or "",
        unit_exp_3=criterias.criteria_explanation_3 or "",
    )

    db.add(problem)
    db.commit()
    db.refresh(problem)

    return problem.id
