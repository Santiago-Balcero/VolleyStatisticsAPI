from typing import Any
from pydantic import BaseModel


class ResponseModel(BaseModel):
    detail: str = None
    # Type Any makes this attribute to be optional
    data: Any