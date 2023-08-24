from fastapi.security.oauth2 import OAuth2PasswordBearer
from fastapi.param_functions import Depends
from jose import jwt
from jose.exceptions import JWTError

import config
from datetime import datetime

from data.dbapi.admins_dbapi.read_queries import check_user_is_admin
from data.dbapi.user_dbapi import read_queries
from data.models.users import Users
from fastapi import Depends, FastAPI, HTTPException, status

from logic.auth.redis_token_cache import RedisTokenCache
from logic.auth.token_cache import TokenCache

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")  # Used to get jwt token from headers


def authenticate_user(email, password):
    user = read_queries.find_by_email(email)
    if not user:
        return False, "Error: login failed. Please check email and password"
    if not user.check_password(password):
        return False, "Error: login failed. please check email and password"
    if user and not user.is_verified:
        return False, "Error: mail verification required"
    return user, ""


def create_access_token(email):
    issue_time = datetime.utcnow()
    issue_time_delta = (issue_time - datetime(1970, 1, 1)).total_seconds()
    issue_time_seconds = int(issue_time_delta)

    data_to_encode = {
        'sub': email,
        'iat': issue_time_seconds,
        'exp': datetime.now() + config.get_expiration_duration()
    }

    encoded_jwt = jwt.encode(
        data_to_encode, config.secret_key, algorithm="HS256")

    token_cache = RedisTokenCache()
    token_cache.add_token(f"{email}_{issue_time_seconds}", encoded_jwt)
    return encoded_jwt


def get_user_from_token(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, config.secret_key, algorithms=['HS256'])
        email = payload.get('sub')
        iat = payload.get('iat')
        if email is None:
            config.default_log.debug("Decoding payload failed")

            raise credentials_exception

        key = f"{email}_{iat}"
        token_cache = RedisTokenCache()
        if not token_cache.verify_token(key):
            config.default_log.debug("Redis: verfiy_token failed")
            raise credentials_exception
    except JWTError as e:
        config.default_log.debug(str(e))
        raise credentials_exception
    user = read_queries.find_by_email(email)
    if user is None:
        config.default_log.debug("User is None")
        raise credentials_exception
    return user



def get_admin_from_token(user: Users = Depends(get_user_from_token)):

    is_admin = check_user_is_admin(user)

    if not is_admin:
        raise HTTPException(status=status.HTTP_401_UNAUTHORIZED,
                            detail="User is not an admin")

    return user