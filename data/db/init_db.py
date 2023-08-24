from fastapi_utils.session import FastAPISessionMaker
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database
import config
from functools import lru_cache

SQLALCHEMY_DATABASE_URL = config.sqlalchemy_database_uri

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, pool_size=100, max_overflow=120
)
if not database_exists(engine.url):
    create_database(engine.url)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

ModelBase = declarative_base()


# See: https://fastapi-utils.davidmontague.xyz/user-guide/session/
def get_db():
    """FastAPI dependency that provides an sqlalchemy session
    """

    yield from _get_fastapi_sessionmaker().get_db()


@lru_cache(maxsize=32)
def _get_fastapi_sessionmaker() -> FastAPISessionMaker:
    fastapi_session_maker = FastAPISessionMaker(config.sqlalchemy_database_uri)
    fastapi_session_maker._cached_engine = engine
    return fastapi_session_maker

