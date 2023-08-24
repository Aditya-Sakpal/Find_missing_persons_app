from pydantic.main import BaseModel


class AddUserDTO(BaseModel):
    email: str
    password: str