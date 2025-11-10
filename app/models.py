from typing import Optional
from dataclasses import dataclass

@dataclass
class ExamProcessRequest:
    file_path: str
    title: str
    description: str

@dataclass
class ExamProcessResponse:
    file_id: str
    status: str

@dataclass
class ExamAnalysisResponse:
    file_id: str
    analysis_report: dict

@dataclass
class ItemAnalysisRequest:
    file_path: str
    query: Optional[str] = None

@dataclass
class Metadata:
    grade: str
    subject: str
    curriculum1: str
    curriculum2: str
    difficulty: str
    difficulty_reason: str
    item_type: str
    points: int
    keywords: str
    content: str

@dataclass
class ItemAnalysisRepsonse:
    item_id: str
    metadata: Metadata

