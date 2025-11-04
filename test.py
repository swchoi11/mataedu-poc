from config import config
from langchain_google_genai import ChatGoogleGenerativeAI
import mimetypes
from langchain_core.messages import HumanMessage
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.runnables import RunnableLambda
from typing import List
import base64
import pandas as pd
import os # os.path.isfile을 사용하기 위해 import

#============================================util
def encode_file_to_uri(file_path: str) -> str | None:
    
    # (★추가★) 파일이 실제로 존재하는지 확인
    if not os.path.isfile(file_path):
        print(f"오류: 파일을 찾을 수 없습니다. (경로: {file_path})")
        return None
        
    mimetype, _ = mimetypes.guess_type(file_path)

    if not mimetype:
        print("파일의 mime 타입을 알 수 없습니다.")
        return None

    try:
        with open(file_path, "rb") as f:
            encode_string = base64.b64encode(f.read()).decode("utf-8")

        # (★수정★) 데이터 URI 형식에서 공백 제거
        return f"data:{mimetype};base64,{encode_string}"

    except Exception as e:
        print(e)

        return None

def dataframe_to_str(file_path: str) -> str | None:
    # (★추가★) 파일이 실제로 존재하는지 확인
    if not os.path.isfile(file_path):
        print(f"오류: 커리큘럼 파일을 찾을 수 없습니다. (경로: {file_path})")
        return None
        
    try:
        data_frame = pd.read_csv(file_path)
        data_str = data_frame.to_string(index=False, max_rows=100) # 데이터가 너무 길어지는 것을 방지
        return data_str
    except Exception as e:
        print(f"커리큘럼 파일 로드 또는 변환 중 오류: {e}")
        return None

#=============================================class
class Curriculum(BaseModel):
    """커리큘럼 정보 모델"""
    grade: str = Field(description="학년")
    subject: str = Field(description="과목")
    main_chap: str = Field(description="대단원")
    mid_chap: str = Field(description="중단원")
    small_chap: str = Field(description="소단원")

class Level(BaseModel):
    main_chap: str = Field(description="대단원")
    mid_chap: str = Field(description="중단원")
    small_chap: str = Field(description="소단원")
    reason: str = Field(description="선택 이유")

class Levels(BaseModel):
    suggestions: List[Level] = Field(description="가장 가능성 있는 라벨 목록(최대2개)")

#==============================================runnable

def create_message(input: dict) -> List[HumanMessage]:

    message = HumanMessage(
        content = [
            {
                "type": "text",
                "text": f"""
                당신은 교육 컨텐츠 분석 전문가 입니다. 
                첨부된 파일의 내용을 분석하여 다음 문제가 커리큘럼에 대응하는지 JSON 형식으로 추출해주세요.

                ---
                커리큘럼 정보:
                {input['curriculum_data']}
                ---
                """
            },
            {
                "type": "image_url",
                "image_url": {"url": input['file_data_uri']}
            }
        ]
    )
    
    return [message]

def create_curriculum(input: dict) -> List[HumanMessage]:
    message = HumanMessage(
        content = [
            {
                "type": "text",
                "text": f"""
                당신은 교육 컨텐츠 분석 전문가입니다. 
                첨부된 파일은 {input['grade']} 수준의 {input['subject']} 과목에 관련된 문제로 분석되었습니다. 
                이 문제에 대한 관련 단원을 라벨링해야합니다. 

                라벨의 목록은 다음과 같습니다. 
                {input['curriculum_data']}

                가장 가능성 있는 라벨을 2개 제안해주세요.
                이유를 함께 제시해주세요.         
                """
            },
            {
                "type": "image_url",
                "image_url": {"url": input['file_data_uri']}
            }
        ]
    )

    return [message]



llm = ChatGoogleGenerativeAI(
    model = config.GEMINI_MODEL,
    google_api_key = config.GEMINI_API_KEY,
    temperature = 0
)

# (★수정★) create_message 함수의 "text" 오타 수정
# 이 함수는 chain1에서만 사용됩니다.
def create_message_fixed(input: dict) -> List[HumanMessage]:
    message = HumanMessage(
        content = [
            {
                "type": "text",
                "text": f"""
                당신은 교육 컨텐츠 분석 전문가 입니다. 
                첨부된 파일의 내용을 분석하여 다음 문제가 커리큘럼에 대응하는지 JSON 형식으로 추출해주세요.

                ---
                커리큘럼 정보:
                {input['curriculum_data']}
                ---
                """
            },
            {
                "type": "image_url",
                "image_url": {"url": input['file_data_uri']}
            }
        ]
    )
    
    return [message]


# (★수정★) chain1이 수정된 함수를 사용하도록 변경
chain1 = (
    RunnableLambda(create_message_fixed) # <-- 수정된 함수 사용
    | llm.with_structured_output(Curriculum)
)


# --- 메인 실행 로직 ---
# 스크립트가 직접 실행될 때만 아래 코드가 동작하도록 __name__ == "__main__" 사용
if __name__ == "__main__":
    file_path = "./data/기출문제/test2.png"
    curriculum_path = "./data/curriculum.csv"

    curriculum_data = dataframe_to_str(curriculum_path)
    if curriculum_data is None:
        raise ValueError("커리큘럼 데이터를 로드하지 못했습니다.")

    file_data_uri = encode_file_to_uri(file_path)
    if file_data_uri is None:
        raise ValueError("파일을 인코딩하지 못했습니다. file_data_uri가 None입니다.")

    print("--- Chain 1 호출 시작 ---")
    input_dict_1 = {"curriculum_data": curriculum_data, "file_data_uri": file_data_uri}
    result_1 = chain1.invoke(input_dict_1)

    print("Chain 1의 결과:", result_1)

    if not result_1:
        raise ValueError("Chain 1의 결과가 None입니다. LLM 호출 또는 파싱에 실패했습니다.")


    print("\n--- Chain 2 호출 시작 ---")
    chain2 = (
        RunnableLambda(create_curriculum)
        | llm.with_structured_output(Levels)
    )

    input_dict_2 = {"grade": result_1.grade, "subject": result_1.subject, "curriculum_data": curriculum_data, "file_data_uri": file_data_uri}
    result_2 = chain2.invoke(input_dict_2)

    print("Chain 2의 결과:", result_2)

