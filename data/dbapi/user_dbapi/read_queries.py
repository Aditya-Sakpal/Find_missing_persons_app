from sqlalchemy.orm import Session
from data.db.init_db import get_db
from data.models.users import Users
from decorators.handle_generic_exception import dbapi_exception_handler


@dbapi_exception_handler
def find_by_email(email, session=None):
    db = session
    if session is None:
        db = next(get_db())
    retval = db.query(Users).filter(Users.email == email).first()
    db.close()
    return retval


@dbapi_exception_handler
def find_user_by_id(id, session=None):
    db = session
    if session is None:
        db = next(get_db())
    retval = db.query(Users).filter(Users.id == id).first()
    db.close()
    return retval


@dbapi_exception_handler
def get_user_id_and_mail(session=None):
    db = session
    if session is None:
        db = next(get_db())

    data = {}
    retval = db.query(Users).all()
    for val in retval:
        data.update({val.id: val.email})
    return data


@dbapi_exception_handler
def find_many_users_by_ids(user_ids, session=None):
    db = session
    if session is None:
        db = next(get_db())

    retval = db.query(Users).filter(Users.id.in_(user_ids)).all()

    return retval

