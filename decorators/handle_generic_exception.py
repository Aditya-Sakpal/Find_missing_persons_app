from functools import wraps
import psycopg2
from requests import session

from sqlalchemy_utils.types.pg_composite import psycopg2
from starlette.responses import JSONResponse

from config import default_log
from data.db.init_db import get_db
from standard_responses.dbapi_exception_response import DBApiExceptionResponse
from fastapi import HTTPException

from standard_responses.standard_json_response import standard_json_response


def frontend_api_generic_exception(function):
    @wraps(function)
    def decorated_function(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except Exception as e:
            default_log.exception(e)


            return standard_json_response(
                message=str(e),
                data={},
                error=True
            )
    return decorated_function
 
 
def dbapi_exception_handler(function):
    @wraps(function)
    def decorated_function(*args, **kwargs):
        db = session
        if session is None:
            db = next(get_db())
        try:
            if not kwargs.get('session'):
                kwargs['session'] = next(get_db())
            db = kwargs['session']
            retval = function(*args, **kwargs)
            if kwargs.get('commit'):
                db.close()
            return retval
        except (psycopg2.errors.OperationalError, psycopg2.errors.UniqueViolation, Exception) as e:
            db.rollback()
            db.close()
            default_log.exception(e)
            return DBApiExceptionResponse(error=str(e), exception_class_name=str(
                type(e)))  # This class resolves to False
        finally:
            if db is not None:
                # If it's a read query, kwargs will not have a commit parameter
                if 'commit' not in kwargs.keys():
                    # Meaning this session was received from previous function
                    # and the session won't be closed if the caller specifically requested so
                    # by setting the `close_session` parameter to False
                    if kwargs.get('session') is not None and kwargs.get(
                            'close_session', True):
                        db.close()
                else:
                    if kwargs['commit']:
                        db.close()
    return decorated_function
