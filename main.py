from fastapi import FastAPI, Depends
import uvicorn
from sqlalchemy.orm import Session

from models import ProblemAnalysisRequest, ProblemAnalysisResponse, ProblemMetadata
from custom_langchain.chains import process_problem_chain
from database.database import get_db, engine, Base
from database.crud import save_problem_analysis

# 데이터베이스 테이블 생성 (entities import 후)
from database import entities
Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.post("/problem", response_model=ProblemAnalysisResponse)
def process_problem(request: ProblemAnalysisRequest, db: Session = Depends(get_db)):
    """
    문제 이미지를 분석하고 결과를 DB에 저장

    1. 랭체인으로 문제 분석
    2. 결과를 데이터베이스에 저장
    3. 응답 반환
    """
    # 1. 랭체인 실행
    analysis_result = process_problem_chain.invoke(
        {"file_data": request.file_data}
    )

    # 2. DB에 저장 (exam_id는 임시로 1 사용, 추후 요청에서 받아야 함)
    problem_id = save_problem_analysis(
        db=db,
        exam_id=1,  # TODO: request에서 exam_id 받도록 수정
        analysis=analysis_result
    )

    # 3. 응답 생성
    return ProblemAnalysisResponse(
        problem_id=str(problem_id),
        metadata=ProblemMetadata(
            grade=analysis_result["curriculum"].grade,
            subject=analysis_result["curriculum"].subject
        )
    )

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)