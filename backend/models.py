from dataclasses import dataclass
from typing import Optional

@dataclass
class ProblemMetadata:
    grade: str
    subject: str
    suggested_curriculum_1: dict
    suggested_curriculum_2: dict
    intent_1: dict
    intent_2: dict
    intent_3: dict
    difficulty: dict
    item_type: str
    points: int
    keywords: str
    content: str

@dataclass
class ProblemAnalysisResponse:
    problem_id: str
    metadata: ProblemMetadata


@dataclass
class ExamAnalysisResponse:
    exam_id: str
    status: str