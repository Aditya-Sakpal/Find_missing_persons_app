from pydantic.main import BaseModel, Optional

from config import default_log


#TODO: Chnage name to DBAPI Exception DTO or something
class DBApiExceptionResponse(BaseModel):
    """Used as a standard response dto for DBApi Exceptions. Used by the
    @dbapi_exception_handler decorator


    Note that it evaluates to false. For example
    if `result = some_dbapi.some_query()` raises an Exception,  it will return
    an object of this class. Then, `result` can be used as:

    ```
    if not result:
        return "some error"
    ```

    OR

    ```
    if result is False:
        return "some error"
    ```

    """
    error: str
    exception_class_name: str
    user_email: Optional[str]

    def __bool__(self):
        # default_log.debug("note: response evauluates to False")
        return False

