from pydantic import BaseModel
from datetime import datetime
from typing import Optional
class CarbonEmissionsModelResponse(BaseModel):
    id: int
    name: str
    year_published: int
    scope_1: Optional[float]
    scope_2: Optional[float]
    scope_3: Optional[float]

    class Config:
        orm_mode = True