from pydantic import BaseModel, HttpUrl
from typing import List, Any, Dict, Optional

class CSVUploadRequest(BaseModel):
    csv_url: HttpUrl

class CSVUploadResponse(BaseModel):
    status: str
    dataset_id: str

class DataQueryRequest(BaseModel):
    dataset_id: str
    filters: Optional[Dict[str, Any]] = None
    date_gt: Optional[str] = None
    date_lt: Optional[str] = None

class DataQueryResponse(BaseModel):
    status: str
    total_results: int
    results: List[Any]
    page: int
    page_size: int