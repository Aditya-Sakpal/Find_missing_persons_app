from pydantic import BaseModel
from typing import Optional

class EchoDTO(BaseModel):
    message: str
