from typing import Literal

from pydantic import BaseModel

ExportFormat = Literal["txt", "pdf"]


class ExportRequest(BaseModel):
    document_id: str
    mode: str
    reading_level: int = 3
    format: ExportFormat = "txt"
