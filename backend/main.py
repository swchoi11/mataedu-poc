import os
import uuid
import shutil
import uvicorn
import tempfile
from sqlalchemy.orm import Session
from fastapi import FastAPI, Depends, File, UploadFile, HTTPException

from database import entities
from utils.process_pdf import image_generator
from database.database import get_db, engine, Base
from utils.process_image import to_base64_data_url
from custom_langchain.chains import process_problem_chain
from models import ProblemAnalysisResponse, ExamAnalysisResponse
from database.crud import save_problem_analysis, save_exam_analysis, get_exam_analysis


Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.post("/exam")
async def process_exam(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    시험지 이미지를 분석하고 결과를 db에 저장
    
    1. 시험지 이미지를 개별 문항 이미지로 파싱
    2. 파싱된 이미지를 minio 에 저장 및 분석
    3. 결과를 데이터베이스에 저장
    4. 응답 반환
    """
    # set 시험지 아이디
    exam_id = uuid.uuid4()

    # pdf 파일 파싱
    original_file_name = file.filename
    if not original_file_name.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="PDF 파일만 업로드할 수 있습니다.")

    save_exam_analysis(
        db=db,
        exam_id=str(exam_id),
        title=original_file_name
    )

    temp_file_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file_path = temp_file.name

            shutil.copyfileobj(file.file, temp_file)

            generator = image_generator(pdf_file_path = temp_file_path,original_file_name = original_file_name)

            for image in generator:
                result = process_problem_chain.invoke(
                    {"file_data":image["base64_data"]}
                )
     
                problem_id = save_problem_analysis(
                    db=db,
                    exam_id=str(exam_id),
                    analysis=result
                )
            return {"exam_id": str(exam_id)}
    finally:
        await file.close()

        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)

@app.post("/problem", response_model=ProblemAnalysisResponse)
async def process_problem(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    문제 이미지를 분석하고 결과를 DB에 저장

    1. 랭체인으로 문제 분석
    2. 결과를 데이터베이스에 저장
    3. 응답 반환
    """
    file_data_bytes = await file.read()

    file_data = to_base64_data_url(file_data_bytes)

    # 1. 랭체인 실행
    analysis_result = await process_problem_chain.ainvoke(
        {"file_data": file_data}
    )

    # 2. DB에 저장 (개별 문항 분석 요청의 경우 시험지 id가 없어서 일단 999로 저장함 -> flag로 변환가능)
    problem_id = save_problem_analysis(
        db=db,
        exam_id="999",
        analysis=analysis_result
    )

    # 3. 응답 생성
    return ProblemAnalysisResponse.from_analysis(
        problem_id=str(problem_id),
        analysis=analysis_result
    )

@app.get("/exam")
async def get_exam_endpoint(exam_id: str, db: Session = Depends(get_db)):
    exam_results = await get_exam_analysis(
        db=db,
        exam_id=exam_id
    )

    return exam_results 

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)