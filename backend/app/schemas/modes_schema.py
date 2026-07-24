from typing import List

from pydantic import BaseModel


class ModeInfo(BaseModel):
    id: str
    label: str
    description: str


class ModesResponse(BaseModel):
    modes: List[ModeInfo]
