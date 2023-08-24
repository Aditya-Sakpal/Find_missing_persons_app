from config import default_log
from data.db.init_db import get_db
from data.dbapi.user_dbapi.dtos.add_user_dto import AddUserDTO
from data.dbapi.user_dbapi.dtos.update_user_dto import UpdateUserDTO
from data.dbapi.user_dbapi.read_queries import find_by_email
from data.models.users import Users
from decorators.handle_generic_exception import dbapi_exception_handler


@dbapi_exception_handler
def add_user(dto: AddUserDTO, session=None, commit=True):
    db = session
    if session is None:
        db = next(get_db())

    user = Users(email=dto.email, password=dto.password)
    default_log.debug(f"Adding user {user.email}")
    db.add(user)
    db.flush()
    retval = user.id

    if commit:
        db.commit()
    return retval


@dbapi_exception_handler
def delete_user(email, session=None, commit=True):
    db = session
    if session is None:
        db = next(get_db())

    user = find_by_email(email)

    default_log.debug(f"Deleting user {email}")
    db.delete(user)
    if commit:
        db.commit()
    return True


@dbapi_exception_handler
def update_user(dto: UpdateUserDTO, session=None, commit=True):
    db = session
    if session is None:
        db = next(get_db())


    user = find_by_email(dto.email)

    if dto.password is not None:
        user.password = dto.password

    if dto.is_verified is not None:
        user.is_verified = dto.is_verified

    default_log.debug(f"Updating user {user.email}")
    db.add(user)
    db.flush()
    retval = user.id
    if commit:
        db.commit()
    return retval

