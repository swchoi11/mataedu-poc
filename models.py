from dataclasses import dataclass
from typing import Optional

@dataclass
class ProblemMetadata:
    grade: str
    subject: str

@dataclass
class ProblemAnalysisRequest:
    file_data: str
    query: Optional[str]

@dataclass
class ProblemAnalysisResponse:
    problem_id: str
    metadata: ProblemMetadata
    