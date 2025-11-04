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
    item_file_path: str
    query: Optional[str] = None

@dattaclass
class ItemAnalysisRepsonse:
    item_id: str
    metadata: dict



