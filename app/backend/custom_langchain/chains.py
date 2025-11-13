from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.runnables import RunnableLambda, RunnableParallel, RunnablePassthrough

from config import config
from custom_langchain.runnables import (
    fetch_curriculum_data,
    fetch_subject_intent_data,
    get_grade_subject_messages,
    get_subject_unit_messages,
    get_problem_intent_messages,
    get_problem_metadata,
    get_poly
)
from custom_langchain.models import Curriculum, UnitSuggestions, IntentSuggestions, MetadataSuggestion, QuestionList

llm = ChatGoogleGenerativeAI(
    model = config.GEMINI_MODEL,
    google_api_key = config.GEMINI_API_KEY,
    temperature = 0
)

# Parser 인스턴스들
curriculum_parser = PydanticOutputParser(pydantic_object=Curriculum)
unit_parser = PydanticOutputParser(pydantic_object=UnitSuggestions)
intent_parser = PydanticOutputParser(pydantic_object=IntentSuggestions)
metadata_parser = PydanticOutputParser(pydantic_object=MetadataSuggestion)
poly_parser = PydanticOutputParser(pydantic_object=QuestionList)

# 1단계: 학년/과목 추출 체인
grade_extraction = (
    RunnableLambda(get_grade_subject_messages)
    | llm
    | curriculum_parser
).with_retry(
    stop_after_attempt=3,
    wait_exponential_jitter=True
)

# 2단계: 교과 단원 추천 체인
curriculum_extraction = (
    RunnableLambda(get_subject_unit_messages)
    | llm
    | unit_parser
).with_retry(
    stop_after_attempt=3,
    wait_exponential_jitter=True
)

# 3단계: 출제 의도/성취기준 추출 체인
criteria_extraction = (
    RunnableLambda(get_problem_intent_messages)
    | llm
    | intent_parser
).with_retry(
    stop_after_attempt=3,
    wait_exponential_jitter=True
)

# 4단계: 메타데이터 추출 체인
metadata_extraction = (
    RunnableLambda(get_problem_metadata)
    | llm
    | metadata_parser
).with_retry(
    stop_after_attempt=3,
    wait_exponential_jitter=True
)

# 최종 포맷팅 함수
def format_final_output(input: dict) -> dict:
    """모든 분석 결과를 최종 포맷으로 변환"""
    return {
        "inferenced_grade": input["inferenced_grade"],
        "unit_suggestions": input["unit_suggestions"],
        "intent_criterias": input["intent_criterias"],
        "metadata": input.get("metadata"),
        "file_data": input["file_data"]
    }

# 문제 영역 추출 체인
poly_extraction = (
    RunnableLambda(get_poly)
    | llm
    | poly_parser
).with_retry(
    stop_after_attempt=3,
    wait_exponential_jitter=True
)


process_problem_chain = (

    RunnablePassthrough.assign(
        curriculum_data = RunnableLambda(fetch_curriculum_data),
        intent_data = RunnableLambda(fetch_subject_intent_data)
    )

    | RunnablePassthrough.assign(
        inferenced_grade = grade_extraction
    )

    | RunnablePassthrough.assign(
        unit_suggestions = curriculum_extraction
    )

    | RunnablePassthrough.assign(
        intent_criterias = criteria_extraction
    )

    | RunnablePassthrough.assign(
        metadata = metadata_extraction
    )

    | RunnableLambda(format_final_output)
)

