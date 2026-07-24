from typing import List

from pydantic import BaseModel


class KeyPointsRequest(BaseModel):
    document_id: str


class KeyPointsResponse(BaseModel):
    document_id: str
    key_points: List[str]
