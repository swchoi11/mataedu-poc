from langchain_core.runnables import (
    RunnableLambda,
    RunnableConfig
)
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import PydanticOutputParser
from typing import List
from custom_langchain.models import QuestionList

def get_grade_subject(input: dict, config: RunnableConfig) -> List[HumanMessage]:
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

def get_subject_unit(input: dict, config: RunnableConfig) -> List[HumanMessage]:
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

def get_problem_intent(input: dict, config: RunnableConfig) -> List[HumanMessage]:
    file_data = input["file_data"]
    curri = input["curriculum"]
    sug = input["suggestions"]

    criteria_data = input["criteria_data"]

    label1 = (f"{sug.main_chap1}>{sug.mid_chap1}>{sug.small_chap1}")
    prompt_inject = ""
    if sug.main_chap2:
        label2 = (f"{sug.main_chap2}>{sug.mid_chap2}>{sug.small_chap2}")
        prompt_inject = "두번째로 가능성 있는 라벨로는 '{label2}'이 추천되었습니다."


    system_prompt = f"""
    당신은 교육 콘텐츠 분석가입니다. 
    첨부된 파일은 {curri.grade} 과정의 {curri.subject} 과목의 문제로 분석되었습니다.
    가장 가능성 있는 라벨로는 {label1}이 추천되었습니다.
    {prompt_inject}첨부된 파일의 내용을 분석하여 이 문제가 학생들에게서 평가하고자 하는 **수행과정(sector), 성취기준(criteria), 성취기준 해설(criteria_explanation)**을 추출해주세요.

    - **최대 3개**까지 추출할 수 있으며, **반드시 1개 이상**은 있어야 합니다.
    - 추출된 내용은 반드시 아래의 '성취기준 목록'에 있는 내용과 일치해야 합니다.
    - Pydantic 스키마에 맞춰 'sector1', 'criteria1', 'criteria_explanation1', 'sector2', 'criteria2', 'criteria_explanation2', 'sector3', 'criteria3', 'criteria_explanation3' 필드를 채워주세요.
    - 만약 2번째나 3번째 성취기준이 없다면 해당 필드(sector2, criteria2...)는 null 또는 빈 값으로 두어야 합니다.

    ----
    성취 기준 목록 :
    {criteria_data}
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

def get_problem_metadata(input: dict, config: RunnableConfig) -> List[HumanMessage]:
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
    5. 핵심 키워드
    6. 파일에서 인식된 문제 텍스트 전체    
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

# output_parser 정의
output_parser = PydanticOutputParser(pydantic_object=QuestionList)

def get_poly(input: dict) -> List[HumanMessage]:
    format_instructions = output_parser.get_format_instructions()
    system_prompt = f"""
    당신은 전문적인 문서 레이아웃 분석가입니다.
    첨부된 이미지는 2단(two-column)으로 구성될 수 있는 시험문제지입니다.
    시험문제지에는 분석해야하는 개별 문항과 함께, 시험 과목, 과정과 관련된 다른 정보들, 페이지 번호 등이 함께 존재합니다. 

    당신의 임무는 페이지에 있는 **모든 개별 문항**만을 식별하는 것입니다.
    다른 텍스트나 설명 없이, 반드시 다음 JSON 스키마를 준수하는 단일 JSON 객체만을 반환해야합니다.
    {format_instructions}
    """
    
    # [수정] 전역 변수가 아닌, input 딕셔너리에서 file_data를 가져옴
    file_data_from_input = input["file_data"]

    message = HumanMessage(
        content = [
            {"type": "text",
            "text":f"이 이미지에서 모든 문제 영역을 분석하고, 요청한 포맷 지침({format_instructions})에 정확히 맞춰 JSON을 반환해주세요."},
            {
                "type": "image_url",
                # [수정] 함수 내부 변수를 사용
                "image_url": {"url": file_data_from_input} 
            }
        ]
    )
    return [SystemMessage(content=system_prompt), message]
