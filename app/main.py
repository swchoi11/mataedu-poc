from fastapi import FastAPI
import uvicorn
from models import ExamProcessRequest, ExamProcessResponse, ExamAnalysisResponse, ItemAnalysisRepsonse, ItemAnalysisRequest, MetadataResult
from custom_langchain.chains import process_exam_chain, process_item_chain
from utils.process_image import encode_image, dataframe_to_str
import uuid

app = FastAPI()

@app.post("/exam", response_model=ExamProcessResponse)
def process_exam_paper(request: ExamProcessRequest):
    # pdf -> 이미지 

    # 이미지 처리

    result = process_exam_chain.invoke(request)
    return ExamProcessResponse(
        file_id=result.file_id,
        status=result.status
    )

@app.get("/exam", response_model=ExamAnalysisResponse)
def get_exam_analization(exam_id: str):
    pass

@app.post("/item", response_model=ItemAnalysisRepsonse)
def process_item(request: ItemAnalysisRequest):
    # 커리큘럼 데이터 삽입 -> db에서 꺼내오는걸로 변경 필요
    curriculum_data = dataframe_to_str("./app/curriculum.csv")
    common_data = {
        "curriculum_data":curriculum_data
    }

    # 이미지 데이터 인코딩해서 입력 -> 체인 안으로 삽입할 필요
    file_data = encode_image(request.file_path)

    # 성취기준 데이터 삽입
    criteria_data = dataframe_to_str('./app/교육과정성취기준.csv')

    result = process_item_chain.invoke(
        {"file_data": file_data,
        "criteria_data": criteria_data},
        config={"configurable": common_data}
    )



    return ItemAnalysisRepsonse(
        item_id=str(uuid.uuid4()),
        metadata=result
    )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
