from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.runnables import RunnableLambda, RunnableParallel, RunnablePassthrough

from config import config
from custom_langchain.models import Curriculum, Suggestions,Metadata, QuestionList
from custom_langchain.runnables import get_grade, get_metadata, get_stage, get_poly, output_parser

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
def format_final_output(input_dict: dict) -> dict:
    metadata = input_dict["metadata"]
    original_curriculum = input_dict["passthrough_data"]["curriculum"]
    suggestions = input_dict["passthrough_data"]["suggestions"]

    grade=original_curriculum.grade
    subject=original_curriculum.subject

    recommendation1 = f"{suggestions.main_chap1}>{suggestions.mid_chap1}>{suggestions.small_chap1}"
    
    recommendation2 = None
    if suggestions.main_chap2 and suggestions.mid_chap2 and suggestions.small_chap2:
        recommendation2 = f"{suggestions.main_chap2}>{suggestions.mid_chap2}>{suggestions.small_chap2}"
            
    return {
        "grade": grade,
        "subject": subject,
        "curriculum1": recommendation1,
        "curriculum2": recommendation2,
        "difficulty": metadata.difficulty,
        "difficulty_reason": metadata.difficulty_reason,
        "item_type": metadata.item_type,
        "points": metadata.points,
        "intent": metadata.intent,
        "keywords": metadata.keywords,
        "content": metadata.content
    }
metadata_extraction = (
    RunnableLambda(get_metadata)
    | llm.with_structured_output(Metadata)
)

step1 = RunnableParallel(
    curriculum = grade_extraction,
    passthrough = RunnablePassthrough()
)

format_for_step2 = RunnableLambda(
    lambda x: {
        "file_data": x["passthrough"]["file_data"],
        "curriculum": x["curriculum"]
    }
)

step2 = RunnableParallel(
    suggestions = curriculum_extraction,
    passthrough = RunnablePassthrough()
)

format_for_step3 = RunnableLambda(
    lambda x: {
        **x["passthrough"],
        "suggestions": x["suggestions"]
    }
)

process_item_chain = (
    step1
    | format_for_step2
    | step2
    | format_for_step3
    | RunnableParallel(
        metadata = metadata_extraction,
        passthrough_data = RunnablePassthrough()
        )
    | RunnableLambda(format_final_output)
    )

