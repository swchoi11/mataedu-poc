import os
import mimetypes
import pandas as pd
import base64

def encode_file_to_uri(file_path: str) -> str | None:
    
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

#============================
from langchain_core.messages import HumanMessage, SystemMessage, BaseMessage
from typing import List

def get_grade(input: dict) -> List[HumanMessage]:
    system_prompt = """
        당신은 교육 콘텐츠 분석가입니다. 
        첨부된 파일의 내용을 분석하여 다움 문제가 어떤 커리큘럼에 대응하는지 json 형식으로 추출해주세요. 
    """
    
    message = HumanMessage(
        content = [
            {
                "type": "text",
                "text": f"""
                        ----
                        커리큘럼 정보:
                        {input['curriculum_data']}
                        ----
                        """
            },
            {
                "type": "image_url",
                "image_url": {"url": input['file_data_uri']}
            }
        ]
    )

    return [SystemMessage(content=system_prompt), message]

from langchain_google_genai import ChatGoogleGenerativeAI
from config import config

llm = ChatGoogleGenerativeAI(
    model = config.GEMINI_MODEL,
    google_api_key = config.GEMINI_API_KEY,
    temperature = 0
)


from langchain_core.runnables import RunnableLambda
from langchain.pydantic_v1 import BaseModel, Field

class Curriculum(BaseModel):
    """커리큘럼 정보 모델"""
    grade: str = Field(description="학년")
    subject: str = Field(description="과목")
    main_chap: str = Field(description="대단원")
    mid_chap: str = Field(description="중단원")
    small_chap: str = Field(description="소단원")



chain1 = (
    RunnableLambda(get_grade)
    | llm.with_structured_output(Curriculum)
)
curriculum_data = dataframe_to_str("./data/curriculum.csv")
file_data_uri = encode_file_to_uri("./data/기출문제/test2.png")
input_dict_1 = {"curriculum_data": curriculum_data, "file_data_uri": file_data_uri}
result_1 = chain1.invoke(input_dict_1)

print(result_1)


def get_stage(input: dict) -> List[HumanMessage]:
    system_prompt = f"""
    당신은 교육 콘텐츠 분석가입니다. 
    첨부된 파일은 {input['grade']} 과정의 {input['subject']} 과목의 문제로 분석되었습니다.
    가장 가능성 있는 라벨로는 {input['main_chap']}>{input['mid_chap']}>{input['small_chap']}이 추천되었습니다.

    첨부된 파일의 내용을 분석하여
    1. 이미 분석된 라벨에 대한 검증을 수행하고
    1-1. 이 라벨이 타당한 경우, 그 다음으로 타당한 라벨을 1개 더 추천해주세요.

    1-2. 이 라벨이 타당하지 않은 경우, 가장 타당한 라벨을 2개 추천해 주세요.
    * 만약 타당한 라벨이 1개만 존재하는 경우 1개만 반환해도 됩니다. 

    * 라벨 목록 안에 있는 라벨로만 제안해주세요.
    """

    message = HumanMessage(
        content = [
            {
                "type": "text",
                "text": f"""
                ---
                라벨 정보 : 
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

    return [SystemMessage(content=system_prompt), message]

from typing import Optional

class Suggestions(BaseModel):
    """단원 제안 모델"""
    main_chap: str = Field(description="대단원")
    mid_chap: str = Field(description="중단원")
    small_chap: str = Field(description="소단원")
    descripition: int = Field(description="라벨이 몇번째 후보인지")
    reason: str = Field(description="해당 라벨을 선택한 이유")

class Levels(BaseModel):
    """단원 제안 목록 모델"""


chain2 = (
    RunnableLambda(get_stage)
    | llm.with_structured_output(Suggestions)
)


input_dict_2 = {"grade": result_1.grade, 
                "subject":result_1.subject,
                "main_chap": result_1.main_chap,
                "mid_chap": result_1.mid_chap,
                "small_chap": result_1.small_chap,
                "curriculum_data": curriculum_data, 
                "file_data_uri": file_data_uri}

result_2 = chain2.invoke(input_dict_2)



def get_metadata(input: dict) -> List[HumanMessage]:
    system_prompt = f"""
    당신은 교육 콘텐츠 분석가입니다. 
    첨부된 파일은 {input['grade']} 과정의 {input['subject']} 과목의 문제로 분석되었습니다.
    가장 가능성 있는 라벨로는 {input['main_chap']}>{input['mid_chap']}>{input['small_chap']}이 추천되었습니다.
    
    첨부된 파일의 내용을 분석하여 다음 메타 데이터를 라벨링해 주세요.

    1. 난이도
    2. 난이도 평가 이유
    3. 문제 유형
    4. 배점 (확인할 수 없는 경우 0)
    5. 출제 의도
    6. 핵심 키워드
    7. 파일에서 인식된 문제 텍스트 전체    
    """

    message = HumanMessage(
        content = [
            {
                "type": "image_url",
                "image_url": {"url": input['file_data_uri']}

            }
        ]
    )

    return [SystemMessage(content=system_prompt), message]


class Metadata(BaseModel):
    difficulty: str = Field(description="")
