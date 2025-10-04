from pydantic import BaseModel
from typing import Dict, Any

class FileReport(BaseModel):
    original_rows: int
    rows_out: int

class ProcessReport(BaseModel):
    summary: Dict[str, Any]
    cleaned_dir: str
