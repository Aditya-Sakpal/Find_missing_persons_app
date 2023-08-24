from fastapi import APIRouter, Depends, Request
from api.test.dtos.echo_dto import EchoDTO
import config
from api.user_management.dtos.add_user_request_dto import AddUserRequestDTO
from api.user_management.dtos.get_user_dto import GetUserDTO
from data.dbapi.admins_dbapi.read_queries import check_user_is_admin
from data.dbapi.user_dbapi import write_queries
from data.dbapi.user_dbapi.dtos.add_user_dto import AddUserDTO
from data.dbapi.user_dbapi.read_queries import find_by_email
from data.models.users import Users
from decorators.handle_generic_exception import frontend_api_generic_exception
from logic.auth.registration import send_verification_mail
from logic.auth.token_management import get_user_from_token
from standard_responses.dbapi_exception_response import DBApiExceptionResponse

user_router = APIRouter(prefix='/users', tags=['users'])


#TODO: Use FastAPI-Users library
@user_router.get("/get/{email}", response_model=GetUserDTO)
@frontend_api_generic_exception
def get_user(email):
    user = find_by_email(email)
    user_out = GetUserDTO(email=user.email)

    return user_out


@user_router.post("/add")
@frontend_api_generic_exception
def add_user(user: AddUserRequestDTO):

    new_user = AddUserDTO(
        email=user.email,
        password=user.password
    )
    if(user.email == "" or user.password  == ""):
        return dict(error="Error: enter mail id and password", response="error"), 400

    old_user = find_by_email(user.email)
    if old_user != None:
        return dict(error="Error: mail id exists please login", response="error"),400

    status = write_queries.add_user(new_user)
    if isinstance(status, DBApiExceptionResponse):
        config.default_log.error(status.error)
        return dict(error="Error: adding user: " + status.error, response="error"),400
    else:
        config.default_log.debug("Added user: " + user.email)
        send_verification_mail(user.email)

    return dict(user=user.email, response="ok"),200


@user_router.post("/delete/{email}")
@frontend_api_generic_exception
def delete_user(email):

    status = write_queries.delete_user(email)

    if isinstance(status, DBApiExceptionResponse):
        config.default_log.error(status.error)
        return dict(error="Error deleting user: " + status.error, response="error")
    else:
        config.default_log.debug("Deleted user: " + email)

    return dict(response="ok")


@user_router.get("/me")
@frontend_api_generic_exception
def get_me(user: Users = Depends(get_user_from_token)):
    is_admin = check_user_is_admin(user)

    return dict(
        id=user.id,
        email=user.email,
        is_admin=is_admin
    )
