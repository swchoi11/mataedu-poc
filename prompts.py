from langchain_core.runnables import (
    RunnableLambda,
    RunnableConfig
)
from langchain_core.messages import HumanMessage, SystemMessage
from typing import List

def get_grade(input: dict, config: RunnableConfig) -> List[HumanMessage]:
    conf = config["configurable"]

    file_data = input["file_data"]

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
                        {conf['curriculum_data']}
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

def get_stage(input: dict, config: RunnableConfig) -> List[HumanMessage]:
    conf = config["configurable"]

    file_data = input["file_data"]
    curri = input["curriculum"]

    system_prompt = f"""
    당신은 교육 콘텐츠 분석가입니다. 
    첨부된 파일은 {curri.grade} 과정의 {curri.subject} 과목의 문제로 분석되었습니다.
    해당 과정의 과목에 포함된 교과단원 중에서 가장 가능성 있는 교과 단원으로는 '{curri.main_chap}>{curri.mid_chap}>{curri.small_chap}'이 추천되었습니다.

    첨부된 파일의 내용을 분석하여
    1. 이미 분석된 커리큘럼에 대한 검증을 수행하고
    1-1. 이 커리큘럼이 타당한 경우, 해당 과정의 과목에서 그 다음으로 타당한 교과단원을 1개 더 추천해주세요.

    1-2. 이 커리큘럼이 타당하지 않은 경우, 가장 타당한 커리큘럼을 2개 추천해 주세요.
         이때 과정과 과목을 먼저 고르고, 이 과정 과목 안에서 가장 타당한 교과단원을 고르도록 하세요.
    * 만약 타당한 커리큘럼이 1개만 존재하는 경우 1개만 반환해도 됩니다. 

    * 커리큘럼 목록 안에 있는 커리큘럼으로만 제안해주세요.
    """

    message = HumanMessage(
        content = [
            {
                "type": "text",
                "text": f"""
                ---
                커리큘럼 정보 : 
                {conf['curriculum_data']}
                ---
                """
            },
            {
                "type": "image_url",
                "image_url": {"url": file_data}
            }
        ]
    )

    return [SystemMessage(content=system_prompt), message]

def get_metadata(input: dict, config: RunnableConfig) -> List[HumanMessage]:
    file_data = input["file_data"]
    curri = input["curriculum"]
    sug = input["suggestions"]

    label1 = (f"{sug.main_chap1}>{sug.mid_chap1}>{sug.small_chap1}")
    prompt_inject = ""
    if sug.main_chap2:
        label2 = (f"{sug.main_chap2}>{sug.mid_chap2}>{sug.small_chap2}")
        prompt_inject = "두번째로 가능성 있는 라벨로는 '{label2}'이 추천되었습니다."
    
    system_prompt = f"""
    당신은 교육 콘텐츠 분석가입니다. 
    첨부된 파일은 {curri.grade} 과정의 {curri.subject} 과목의 문제로 분석되었습니다.
    가장 가능성 있는 라벨로는 {label1}이 추천되었습니다.
    {prompt_inject}
    첨부된 파일의 내용을 분석하여 다음 메타 데이터를 라벨링해 주세요.

    1. 난이도 : 해당 과정의 과목에 있는 학생이 배우기에 얼마나 어려운지에 대한 판단
    2. 난이도 평가 이유
    3. 문제 유형
    4. 배점 (확인할 수 없는 경우 0)
    5. 출제 의도 : 학생이 어떤 개념을 알아야 하는지
    6. 핵심 키워드
    7. 파일에서 인식된 문제 텍스트 전체    
    """

    message = HumanMessage(
        content = [
            {
                "type": "image_url",
                "image_url": {"url": file_data}

            }
        ]
    )

    return [SystemMessage(content=system_prompt), message]
