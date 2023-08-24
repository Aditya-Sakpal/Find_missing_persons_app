from fastapi import FastAPI, Request
from fastapi.applications import RequestValidationError
from standard_responses.standard_json_response import standard_json_response
from fastapi.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles
import os
from auth import signup,signin
from handle_data import handle_data
from dotenv import dotenv_values

os.environ['AWS_ACCESS_KEY_ID'] = dotenv_values('.env')['AWS_ACCESS_KEY_ID']
os.environ['AWS_SECRET_ACCESS_KEY'] =dotenv_values('.env')['AWS_SECRET_ACCESS_KEY']

app = FastAPI()

app.include_router(signup.router)
app.include_router(signin.router)
app.include_router(handle_data.router)

@app.exception_handler(RequestValidationError)
async def default_exception_handler(request: Request, exc: RequestValidationError):
    return standard_json_response(
        status_code=200,
        data={},
        error=True,
        message=str(exc)
    )

templates=Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")

img_data=None
faceId=None
# HTML form endpoint


@app.get("/")
def home(request: Request):
    face_detected=None
    matched=None
    auth=None
    invalid=None
    return templates.TemplateResponse("index.html", {"request": request,"face_detected":face_detected,"matched":matched,"auth":auth,"invalid":invalid})


def create_app():
    return app



