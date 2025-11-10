from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.runnables import RunnableLambda, RunnableParallel, RunnablePassthrough

from config import config
from custom_langchain.models import Curriculum, Suggestions,Metadata, QuestionList, Criteria
from custom_langchain.runnables import get_grade, get_metadata, get_stage, get_poly, output_parser, get_criteria

llm = ChatGoogleGenerativeAI(
    model = config.GEMINI_MODEL,
    google_api_key = config.GEMINI_API_KEY,
    temperature = 0
)

# 시험지 처리 체인
process_exam_chain = (
    RunnableLambda(get_poly)
    | llm
    | output_parser
)


# 메타 분석 체인
grade_extraction = (
    RunnableLambda(get_grade)
    | llm.with_structured_output(Curriculum)
)

curriculum_extraction = (
    RunnableLambda(get_stage)
    | llm.with_structured_output(Suggestions)
)

criteria_extraction = (
    RunnableLambda(get_criteria)
    | llm.with_structured_output(Criteria)
)

metadata_extraction = (
    RunnableLambda(get_metadata)
    | llm.with_structured_output(Metadata)
)


# 출력 형식 정의

def format_final_output(input_dict: dict) -> dict:
    metadata = input_dict["metadata"]
    original_curriculum = input_dict["curriculum"]
    suggestions = input_dict["suggestions"]
    criterias = input_dict.get("criterias")

    grade=original_curriculum.grade
    subject=original_curriculum.subject

    recommendation1 = f"{suggestions.main_chap1}>{suggestions.mid_chap1}>{suggestions.small_chap1}"
    
    recommendation2 = None
    if suggestions.main_chap2 and suggestions.mid_chap2 and suggestions.small_chap2:
        recommendation2 = f"{suggestions.main_chap2}>{suggestions.mid_chap2}>{suggestions.small_chap2}"
    
    print(criterias)

    return {
        "grade": grade,
        "subject": subject,
        "curriculum1": recommendation1,
        "curriculum2": recommendation2,
        "difficulty": metadata.difficulty,
        "difficulty_reason": metadata.difficulty_reason,
        "item_type": metadata.item_type,
        "points": metadata.points,
        "keywords": metadata.keywords,
        "content": metadata.content,

        "sector1": getattr(criterias, "sector1", None),
        "criteria1": getattr(criterias, "criteria1", None),
        "criteria_explanation1": getattr(criterias, "criteria_exp1", None),
        "sector2": getattr(criterias, "sector2", None),
        "criteria2": getattr(criterias, "criteria2", None),
        "criteria_explanation2": getattr(criterias, "criteria_exp2", None),
        "sector3": getattr(criterias, "sector3", None),
        "criteria3": getattr(criterias, "criteria3", None),
        "criteria_explanation3": getattr(criterias, "criteria_exp3", None),

    }


# step1 = RunnableParallel(
#     curriculum = grade_extraction,
#     passthrough = RunnablePassthrough()
# )

# format_for_step2 = RunnableLambda(
#     lambda x: {
#         "file_data": x["passthrough"]["file_data"],
#         "curriculum": x["curriculum"]              
#     }
# )

# step2 = RunnableParallel(
#     suggestions = curriculum_extraction,
#     passthrough = RunnablePassthrough()
# )

# format_for_step3 = RunnableLambda(
#     lambda x: {
#         **x["passthrough"],
#         "suggestions": x["suggestions"]
#     }
# )



# process_item_chain = (
#     step1
#     | format_for_step2
#     | step2
#     | format_for_step3
#     | RunnableParallel(
#         metadata = metadata_extraction,
#         passthrough_data = RunnablePassthrough()
#         )
#     | RunnableLambda(format_final_output)
#     )

process_item_chain = RunnablePassthrough() | (
    # 1. 커리큘럼 키를 딕셔너리에 추가
    RunnablePassthrough.assign(
        curriculum = grade_extraction
    )

    # 2. suggestion 키를 딕셔너리에 추가
    | RunnablePassthrough.assign(
        suggestions = curriculum_extraction
    )

    # 3. criterias 키를 딕셔너리에 추가
    | RunnablePassthrough.assign(
        criterias = criteria_extraction
    )

    # 4. metadata키를 딕셔너리에 추가
    | RunnablePassthrough.assign(
        metadata = metadata_extraction
    )

    # 5. 모든 키가 누적된 딕셔너리를 최종 포맷팅
    | RunnableLambda(format_final_output)
)
