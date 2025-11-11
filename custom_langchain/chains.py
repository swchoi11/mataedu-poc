from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.runnables import RunnableLambda, RunnableParallel, RunnablePassthrough

from config import config

llm = ChatGoogleGenerativeAI(
    model = config.GEMINI_MODEL,
    google_api_key = config.GEMINI_API_KEY,
    temperature = 0
)

process_problem_chain = (
    RunnablePassthrough() 
    
    | RunnablePassthrough.assign(
        curriculum_data = RunnableLambda(fetch_curriculum_data)
        criteria_Data = RunnableLambda(fetch_subject_intent_data)
    )

    # 1. 커리큘럼 키를 딕셔너리에 추가
    | RunnablePassthrough.assign(
        inferenced_grade = grade_extraction
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