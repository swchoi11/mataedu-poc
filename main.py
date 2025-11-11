from fastapi import FastAPI
from uvicorn

from models import ProblemAnalysisRequest, ProblemAnalysisResponse
from custom_langchain.chains import process_problem_chain

app = FastAPI()

@app.post("/problem", response_model=ProblemAnalysisResponse)
def process_problem(request: ProblemAnalysisRequest):
    response_meta = process_problem_chain.invoke(
        {"file_data": file_data},
    )

    return ProblemAnalysisResponse(
        problem_id = response_meta.problem_id,
        problem_id = response_meta.metadata
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)