from pydantic.main import BaseModel, Optional


class UpdateUserDTO(BaseModel):
    email: str
    password: Optional[str]
    is_verified: Optional[bool]