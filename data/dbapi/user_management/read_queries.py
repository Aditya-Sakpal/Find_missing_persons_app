from sqlalchemy.orm import Session
from data.db.init_db import get_db
from data.models.users import Users


def find_by_email(email):
    db = next(get_db())
    retval = db.query(Users).filter(Users.email == email).first()
    db.close()
    return retval
