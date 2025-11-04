from fastapi import fastapi
from models import ExamProcessRequest, ExamProcessResponse, ExamAnalysisResponse, ItemAnalysisRepsonse, ItemAnalysisRequest

app = FastAPI()

@app.post("/exam", response_model=ExamProcessResponse)
def process_exam_paper(request: ExamProcessRequest):
    pass

@app.get("/exam", response_model=ExamAnalysisResponse)
def get_exam_analization(exam_id: str):
    pass



@app.post("/item", response_model=ItemAnalysisRepsonse)
def process_item(request: ItemAnalysisRequest):
    pass

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)