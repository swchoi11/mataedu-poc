from sqlalchemy.orm import Session
from typing import Optional, Any, List
from collections import defaultdict
from database.entities import Problem, Exam, Curriculum, SubjectUnit
from custom_langchain.models import Curriculum as CurriculumModel, UnitSuggestions, IntentSuggestions, MetadataSuggestion
from fastapi import HTTPException
from database.database import get_db

def save_problem_analysis(
    db: Session,
    exam_id: str,
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
    curriculum: CurriculumModel = analysis["inferenced_grade"]
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
        difficulty=metadata.difficulty if metadata else "",
        difficulty_reason=metadata.difficulty_reason if metadata else "",
        item_type=metadata.item_type if metadata else "",
        points=metadata.points if metadata else 0,
        keywords=metadata.keywords if metadata else "",
        content=metadata.content if metadata else "",

        # 출제 의도/성취기준 1
        sector_1=criterias.sector_1,
        criteria_1=criterias.criteria_1,
        criteria_exp_1=criterias.criteria_explanation_1,

        # 출제 의도/성취기준 2 (Optional)
        sector_2=criterias.sector_2 or "",
        criteria_2=criterias.criteria_2 or "",
        criteria_exp_2=criterias.criteria_explanation_2 or "",

        # 출제 의도/성취기준 3 (Optional)
        sector_3=criterias.sector_3 or "",
        criteria_3=criterias.criteria_3 or "",
        criteria_exp_3=criterias.criteria_explanation_3 or "",
    )

    db.add(problem)
    db.commit()
    db.refresh(problem)

    return problem.id

def save_exam_analysis(    
        db: Session,
        exam_id: str,
        title: str) -> None:

    exam = Exam(
        exam_id=exam_id,
        title=title
    )
    
    db.add(exam)
    db.commit()
    db.refresh(exam)

    return exam_id

async def get_exam_analysis(db: Session, exam_id: str):
    """
    시험지 ID로 모든 문제를 조회하고 요약 통계를 반환

    Args:
        db: 데이터베이스 세션
        exam_id: 시험지 ID

    Returns:
        시험지 요약 통계 및 개별 문항 목록
    """
    try:
        problems = db.query(Problem).filter(Problem.exam_id == exam_id).all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    if not problems:
        raise HTTPException(status_code=404, detail=f"No problems found for exam_id: {exam_id}")

    # 개별 문항 목록 (최종 응답에 포함될 리스트)
    problem_list_response = []

    # 집계 데이터용 (과목별, 난이도별, 유형별 카운트)
    problems_by_subject = defaultdict(int)
    problems_by_difficulty = defaultdict(int)
    problems_by_type = defaultdict(int)

    # 요약 통계용 (평균 계산을 위한 합계)
    total_problems = len(problems)
    sum_points = 0

    # DB에서 가져온 'problems' 리스트를 단 한 번만 순회
    for problem in problems:

        # 개별 문항 목록에 추가
        problem_list_response.append({
            "problem_id": problem.id,
            "grade": problem.grade,
            "subject": problem.subject,
            "main_chapter_1": problem.main_chapter_1,
            "sub_chapter_1": problem.sub_chapter_1,
            "lesson_chapter_1": problem.lesson_chapter_1,
            "reason_1": problem.reason_1,
            "main_chapter_2": problem.main_chapter_2,
            "sub_chapter_2": problem.sub_chapter_2,
            "lesson_chapter_2": problem.lesson_chapter_2,
            "reason_2": problem.reason_2,
            "difficulty": problem.difficulty,
            "difficulty_reason": problem.difficulty_reason,
            "points": problem.points,
            "item_type": problem.item_type,
            "keywords": problem.keywords.split(",") if problem.keywords else [],
            "content": problem.content,
            "sector_1": problem.sector_1,
            "criteria_1": problem.criteria_1,
            "criteria_exp_1": problem.criteria_exp_1,
            "sector_2": problem.sector_2,
            "criteria_2": problem.criteria_2,
            "criteria_exp_2": problem.criteria_exp_2,
            "sector_3": problem.sector_3,
            "criteria_3": problem.criteria_3,
            "criteria_exp_3": problem.criteria_exp_3,
            "created_time": problem.created_time.isoformat() if problem.created_time else None
        })

        # 집계 데이터: 카테고리별 카운트 증가
        problems_by_subject[problem.subject] += 1
        problems_by_difficulty[problem.difficulty] += 1
        problems_by_type[problem.item_type] += 1

        # 요약 통계: 평균 계산용 값 누적
        sum_points += problem.points if problem.points else 0

    # 평균 계산
    average_points = round(sum_points / total_problems, 2) if total_problems > 0 else 0

    # 최종 응답 JSON 반환
    return {
        # 1. 요약 통계
        "total_problems": total_problems,
        "total_points": sum_points,
        "average_points": average_points,

        # 2. 집계 데이터
        "problems_by_subject": dict(problems_by_subject),
        "problems_by_difficulty": dict(problems_by_difficulty),
        "problems_by_type": dict(problems_by_type),

        # 3. 개별 문항 목록
        "problem_list": problem_list_response
    }

def fetch_curriculum_data(input: Optional[Any] = None) -> str:
    """커리큘럼 데이터를 데이터베이스에서 가져오기"""
    db: Session = next(get_db())

    try:
        results: List[Curriculum] = db.query(Curriculum).all()

    finally:
        db.close()

    output_lines = ["학년,과목,대단원번호,대단원,중단원번호,중단원,소단원번호,소단원"]

    for item in results:
        line = f"{item.grade},{item.subject},{item.no_main_chapter},{item.main_chapter},{item.no_sub_chapter},{item.sub_chapter},{item.no_lesson_chapter},{item.lesson_chapter}"

        output_lines.append(line)

    return "\n".join(output_lines)

def fetch_subject_intent_data(input: Optional[Any] = None) -> str:
    """성취기준 데이터를 데이터베이스에서 가져오기"""
    db: Session = next(get_db())

    try:
        results: List[SubjectUnit] = db.query(SubjectUnit).all()

    finally:
        db.close()

    output_lines  = ["수행과정, 성취기준, 성취기준해설"]

    for item in results:
        line = f"{item.sector}, {item.criteria}, {item.criteria_exp}"

        output_lines.append(line)

    return "\n".join(output_lines)