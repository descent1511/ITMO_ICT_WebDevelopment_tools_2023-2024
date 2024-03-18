import datetime
from decouple import config
from fastapi import Depends, Security, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from models import User
from passlib.context import CryptContext
import jwt
from starlette import status
from db import get_session

ACCESS_TOKEN_EXPIRE_MINUTES = 30  
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7 
ALGORITHM = "HS256"
JWT_SECRET_KEY = config('JWT_SECRET_KEY')  
JWT_REFRESH_SECRET_KEY = config('JWT_REFRESH_SECRET_KEY')

class AuthHandler:
    security = HTTPBearer()
    pwd_context = CryptContext(schemes=['bcrypt'])
   

    def get_password_hash(self, password):
        return self.pwd_context.hash(password)

    def verify_password(self, pwd, hashed_pwd):
        return self.pwd_context.verify(pwd, hashed_pwd)

    def access_token(self, user_id):
        payload = {
            'exp': datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
            'iat': datetime.datetime.now(datetime.UTC),
            'sub': user_id
        }

        return jwt.encode(payload, JWT_SECRET_KEY, algorithm=ALGORITHM)

    def refresh_token(self, user_id): 
        payload = {
            'exp': datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES),
            'iat': datetime.datetime.now(datetime.UTC),
            'sub': user_id
        }

        return jwt.encode(payload, JWT_REFRESH_SECRET_KEY, algorithm=ALGORITHM)
    
   
    def decode_token(self, token):
        try:
            print(token)
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
            return payload['sub']
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail='Expired signature')
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail='Invalid token')

    def auth_wrapper(self, auth: HTTPAuthorizationCredentials = Security(security)):
        return self.decode_token(auth.credentials)

    def get_current_user(self, auth: HTTPAuthorizationCredentials = Security(security),session=Depends(get_session)):
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Could not validate credentials'
        )
        username = self.decode_token(auth.credentials)
        if username is None:
            raise credentials_exception
        user = session.query(User).filter(User.username == username).first()
        if user is None:
            raise credentials_exception
        return user