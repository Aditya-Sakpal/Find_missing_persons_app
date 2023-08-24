from pydantic.main import BaseModel


class AddUserRequestDTO(BaseModel):
    email: str
    password: str
