from data.db.init_db import get_db
from data.models.admins import Admins
from data.models.users import Users
from decorators.handle_generic_exception import dbapi_exception_handler


@dbapi_exception_handler
def check_user_is_admin(user: Users, session=None):

    db = session
    if session is None:
        db = next(get_db())

    admins = db.query(Admins).filter(Admins.user_id == user.id).all()

    if len(admins):
        return True
    return False

