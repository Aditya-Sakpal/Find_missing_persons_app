from fastapi import APIRouter, Depends, Request
from api.test.dtos.echo_dto import EchoDTO
import config
from config import default_log


router = APIRouter(prefix='/test', tags=['test'])

@router.get('/healthcheck')
def healthcheck(request: Request):

    return dict(response="ok")


@router.post('/echo')
def echo(request: Request, echoDTO: EchoDTO):
    return dict(message=echoDTO.message)
