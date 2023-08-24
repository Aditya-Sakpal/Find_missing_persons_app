from pydantic.main import BaseModel


class LoginUserDTO(BaseModel):
    email: str
    password: str