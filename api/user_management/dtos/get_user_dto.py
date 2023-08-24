from pydantic.main import BaseModel, Optional


class GetUserDTO(BaseModel):
    email: str
