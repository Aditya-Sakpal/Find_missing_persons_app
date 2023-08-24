from starlette.responses import JSONResponse
from typing import Dict, Union, List


def standard_json_response(message: str, error: bool,
                           data: Union[List, Dict, str],
                           status_code: int = 200):
    return JSONResponse(
        content={
            'message': message,
            'error': error,
            'data': data
        },
        status_code=status_code
    )
