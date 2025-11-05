from prompts import get_grade, get_metadata, get_stage
from langchain_google_genai import ChatGoogleGenerativeAI
from config import config
from models import Curriculum, Suggestions,Metadata

from langchain_core.runnables import RunnableLambda, RunnableParallel, RunnablePassthrough

llm = ChatGoogleGenerativeAI(
    model = config.GEMINI_MODEL,
    google_api_key = config.GEMINI_API_KEY,
    temperature = 0
)

grade_extraction = (
    RunnableLambda(get_grade)
    | llm.with_structured_output(Curriculum)
)

curriculum_extraction = (
    RunnableLambda(get_stage)
    | llm.with_structured_output(Suggestions)
)

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

final_chain = (
    step1
    | format_for_step2
    | step2
    | format_for_step3
    | metadata_extraction
)
