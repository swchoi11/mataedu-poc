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
class MetadataResult:
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
    sector1: str
    criteria1: str
    creteria_explanation1: str
    sector2: str
    criteria2: str
    creteria_explanation2: str
    sector3: str
    criteria3: str
    creteria_explanation3: str

@dataclass
class ItemAnalysisRepsonse:
    item_id: str
    metadata: MetadataResult

