from database.database import get_db
from sqlalchemy.orm import Session
from typing import List, Optional, Any
from database.entities import Curriculum, SubjectUnit

from langchain_core.runnables import RunnableLambda
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.messages import HumanMessage, SystemMessage

from .models import Curriculum as CurriculumModel, UnitSuggestions, IntentSuggestions, MetadataSuggestion

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
        line = f"{item.sector}, {item.unit}, {item.unit_exp}"

        output_lines.append(line)

    return "\n".join(output_lines)

def get_grade_subject_messages(input: dict) -> List[HumanMessage]:
    """메시지 생성 함수 - 체인에서 사용"""
    file_data = input["file_data"]
    curriculum_data = input["curriculum_data"]

    # Parser 인스턴스 생성
    parser = PydanticOutputParser(pydantic_object=CurriculumModel)

    system_prompt = f"""당신은 교육 콘텐츠 분석가입니다.
첨부된 파일의 내용을 분석하여 다음 문제가 어떤 커리큘럼에 대응하는지 추출해주세요.

{parser.get_format_instructions()}
"""

    message = HumanMessage(
        content = [
            {
                "type": "text",
                "text": f"""
----
커리큘럼 정보:
{curriculum_data}
----
"""
            },
            {
                "type":"image_url",
                "image_url": {"url": file_data}
            }
        ]
    )

    return [SystemMessage(content=system_prompt), message]

def get_subject_unit_messages(input: dict) -> List[HumanMessage]:
    """메시지 생성 함수 - 체인에서 사용"""
    file_data = input["file_data"]
    inferenced_grade = input["inferenced_grade"]
    curriculum_data = input["curriculum_data"]

    # Parser 인스턴스 생성
    parser = PydanticOutputParser(pydantic_object=UnitSuggestions)

    system_prompt = f"""당신은 교육 콘텐츠 분석가입니다.
첨부된 파일은 {inferenced_grade.grade} 과정의 {inferenced_grade.subject} 과목의 문제로 분석되었습니다.
해당 과정의 과목에 포함된 교과 단원 중에서 가장 가능성 있는 교과 단원으로는 '{inferenced_grade.main_chapter}>{inferenced_grade.sub_chapter}>{inferenced_grade.lesson_chapter}'가 제안되었습니다.

첨부된 파일의 내용을 분석하여 다음 단계를 수행하세요.
1. 이미 분석된 커리큘럼에 대한 검증을 수행하세요

2. 이 커리큘럼이 타당한 경우
2-1. 해당 과정의 과목에서 그 다음으로 타당한 교과 단원을 1개 더 추천해주세요.

3. 이 커리큘럼이 타당하지 않은 경우
3-1. 타당한 과정과 과목을 선택하세요
3-2. 이 과정과 과목에 해당되는 교과 단원 중에서 가장 타당한 교과 단원을 고르세요.
3-3. 그 다음으로 타당한 교과단원을 1개 더 고르세요.

* 주의사항
    - 2-1과 3-3의 단계에서 타당한 교과단원을 찾을 수 없다면 생략해도 됩니다.
    - 커리큘럼 목록 안에 있는 교과 단원으로만 제안해주세요.
    - 교과단원이란 대단원>(중단원)>(소단원)으로 이뤄진 과정을 말합니다.
    - **중요**: 커리큘럼 목록에서 소단원(lesson_chapter)이 비어있거나 null인 경우, 해당 중단원명을 소단원명으로 그대로 사용하세요. 절대 null이나 빈 값으로 두지 마세요.
    - lesson_chapter_1과 lesson_chapter_2는 반드시 구체적인 문자열 값이어야 합니다.

{parser.get_format_instructions()}
"""

    message = HumanMessage(
        content=[
            {
                "type": "text",
                "text": f"""
----
커리큘럼 정보 :
{curriculum_data}
----
"""
            },
            {
                "type":"image_url",
                "image_url": {"url":file_data}
            }
        ]
    )

    return [SystemMessage(content=system_prompt), message]

def get_problem_intent_messages(input: dict) -> List[HumanMessage]:
    """메시지 생성 함수 - 체인에서 사용"""
    file_data = input["file_data"]
    inferenced_grade = input["inferenced_grade"]
    unit_suggestions = input["unit_suggestions"]
    intent_data = input["intent_data"]

    # Parser 인스턴스 생성
    parser = PydanticOutputParser(pydantic_object=IntentSuggestions)

    # 교과 단원 추천 결과 변환
    inf_unit_1 = f"{unit_suggestions.main_chapter_1}>{unit_suggestions.sub_chapter_1}>{unit_suggestions.lesson_chapter_1}"
    prompt_inject = ""
    if unit_suggestions.main_chapter_2:
        inf_unit_2 = f"{unit_suggestions.main_chapter_2}>{unit_suggestions.sub_chapter_2}>{unit_suggestions.lesson_chapter_2}"
        prompt_inject = f"두번째로 가능성 있는 라벨로는 '{inf_unit_2}'이 추천되었습니다."

    system_prompt = f"""당신은 교육 콘텐츠 분석가입니다.
첨부된 파일은 {inferenced_grade.grade} 과정의 {inferenced_grade.subject} 과목의 문제로 분석되었습니다.

가장 가능성 있는 교과 단원으로는 '{inf_unit_1}' 이 추천되었습니다.
{prompt_inject}

첨부된 파일의 내용을 분석하여 이 문제가 학생들에게서 평가하고자하는 수행과정, 성취기준, 성취기준 해설을 추출해주세요.

* 주의 사항
    - 최대 3개까지 추출할 수 있으며, 반드시 1개 이상은 있어야합니다.
    - 반드시 성취기준 목록의 내용 안에서만 추출해야합니다.
    - 만약 2번째나 3번째 성취기준이 없다면 해당 필드들은 null 또는 빈 값으로 두어야 합니다.

{parser.get_format_instructions()}
"""

    message = HumanMessage(
        content = [
            {
                "type": "text",
                "text": f"""
----
성취기준 목록:
{intent_data}
----
"""
            },
            {
                "type": "image_url",
                "image_url": {"url": file_data}
            }
        ]
    )

    return [SystemMessage(content=system_prompt), message]

def get_problem_metadata(input: dict) -> List[HumanMessage]:
    """메타 데이터 생성 함수"""
    file_data = input["file_data"]
    inferenced_grade = input["inferenced_grade"]
    unit_suggestions = input["unit_suggestions"]
    intent_data = input["intent_data"]

    # Parser 인스턴스 생성
    parser = PydanticOutputParser(pydantic_object=MetadataSuggestion)

    # 교과 단원 추천 결과 변환
    inf_unit_1 = f"{unit_suggestions.main_chapter_1}>{unit_suggestions.sub_chapter_1}>{unit_suggestions.lesson_chapter_1}"
    prompt_inject = ""
    if unit_suggestions.main_chapter_2:
        inf_unit_2 = f"{unit_suggestions.main_chapter_2}>{unit_suggestions.sub_chapter_2}>{unit_suggestions.lesson_chapter_2}"
        prompt_inject = f"두번째로 가능성 있는 라벨로는 '{inf_unit_2}'이 추천되었습니다."

    system_prompt = f"""당신은 교육 콘텐츠 분석가입니다.
첨부된 파일은 {inferenced_grade.grade} 과정의 {inferenced_grade.subject} 과목의 문제로 분석되었습니다.

가장 가능성 있는 교과 단원으로는 '{inf_unit_1}' 이 추천되었습니다.
{prompt_inject}

첨부된 파일의 내용을 분석하여 다음 메타 데이터를 라벨링해주세요.

1. difficulty : 난이도 - 해당 과정의 과목에 있는 학생이 배우기에 얼마나 어려운지 판단. 반드시 '상', '중', '하' 중 하나로만 답해주세요.
2. difficulty_reason : 난이도 평가 이유 - 위에서 선택한 난이도에 대한 구체적인 근거
3. item_type : 문제 유형 - 반드시 '5지선다', '조합형', '단답형', '서술형' 중 하나로만 답해주세요.
4. points : 배점 - 문제에 표시된 배점 (확인할 수 없는 경우 0)
5. keywords : 핵심 키워드 - 쉼표로 구분된 키워드들 (예: '도형의 대칭이동, 최단 거리, 직선의 방정식')
6. content : 파일에서 인식된 문제 텍스트 전체

{parser.get_format_instructions()}
"""

    message = HumanMessage(
        content = [
            {
                "type": "text",
                "text": f"""
----
문제 이미지를 분석하여 위 메타 데이터를 추출해주세요.
----
"""
            },
            {
                "type": "image_url",
                "image_url": {"url": file_data}
            }
        ]
    )

    return [SystemMessage(content=system_prompt), message]


def get_poly(input: dict) -> List[HumanMessage]:
    from custom_langchain.models import QuestionList

    file_data_from_input = input["file_data"]

    # Parser 인스턴스 생성
    parser = PydanticOutputParser(pydantic_object=QuestionList)

    system_prompt = f"""당신은 전문적인 문서 레이아웃 분석가입니다.
첨부된 이미지는 2단(two-column)으로 구성될 수 있는 시험문제지입니다.
시험문제지에는 분석해야하는 개별 문항과 함께, 시험 과목, 과정과 관련된 다른 정보들, 페이지 번호 등이 함께 존재합니다.

당신의 임무는 페이지에 있는 **모든 개별 문항**만을 식별하는 것입니다.

{parser.get_format_instructions()}

중요:
- question_number: 문제 번호를 문자열로 (예: "8", "9", "10")
- x_min, y_min, x_max, y_max: 0.0~1.0 사이의 정규화된 상대 좌표값
- 절대 픽셀 좌표를 사용하지 마세요
"""

    message = HumanMessage(
        content = [
            {
                "type": "image_url",
                "image_url": {"url": file_data_from_input}
            }
        ]
    )
    return [SystemMessage(content=system_prompt), message]