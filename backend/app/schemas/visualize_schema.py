from typing import List, Literal, Optional

from pydantic import BaseModel


class VisualizeRequest(BaseModel):
    document_id: str


class ChartData(BaseModel):
    labels: List[str]
    values: List[float]
    unit: Optional[str] = None


class VisualizeResponse(BaseModel):
    document_id: str
    visualization_type: Literal["flowchart", "bar_chart", "pie_chart", "none"]
    title: str
    mermaid_code: Optional[str] = None
    chart_data: Optional[ChartData] = None
    explanation: str
