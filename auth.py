import time
import jwt
from jwt.exceptions import DecodeError
from sqlalchemy.orm import Session
from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.status import HTTP_403_FORBIDDEN
from decouple import config

from schemas import UserLogin
from models import User
from database import SessionLocal

JWT_SECRET = config("SECRET")
JWT_ALGORITHM = config("ALGORITHM")

def is_authenticated(data: UserLogin, session: Session) -> bool:
    user = session.query(User).filter(User.username == data.username).first()
    if (not user) or (user.password != data.password):
        return False
    return True

def jwt_encode(user_id: int) -> str:
    payload = {
        "user_id": user_id,
        "expires": time.time() + 600
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    return token

def jwt_decode(token: str) -> dict:
    try:
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return decoded_token if decoded_token["expires"] >= time.time() else None
    except DecodeError:
        raise DecodeError

def get_jwt(request: Request) -> str:

    authorization = request.headers.get("Authorization")
    unpacked_auth: list = authorization.split(" ")
    return unpacked_auth[1]

def get_user_from_jwt(jwt_token: str, session: Session) -> int:

    try:
        decoded_token = jwt_decode(jwt_token)
    except DecodeError:
        raise DecodeError

    user_id = decoded_token["user_id"]
    return user_id

class UserPermission(HTTPBearer):

    def __init__(self, auto_error: bool = True):
        super(UserPermission, self).__init__(auto_error=auto_error)

    async def __call__(self , request: Request):
        credentials: HTTPAuthorizationCredentials = await super(UserPermission, self).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Invalid authentication scheme.")
            if not self.verify_jwt(credentials.credentials):
                raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Invalid token or expired token.")
            return credentials.credentials
        else:
            raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Invalid authorization code.")

    def verify_jwt(self, jwt_token: str) -> bool:
        session = SessionLocal()
        decoded_token = jwt_decode(token=jwt_token)
        user = session.query(User).get(decoded_token["user_id"])
        if user:
            return True
        return False

