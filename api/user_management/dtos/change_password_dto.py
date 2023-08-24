from pydantic.main import BaseModel


class ChangePasswordDTO(BaseModel):
    token: str
    password1: str
    password2: str
