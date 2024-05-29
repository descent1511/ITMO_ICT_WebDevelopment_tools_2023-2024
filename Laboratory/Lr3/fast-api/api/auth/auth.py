from fastapi import Depends, HTTPException, APIRouter,  status,BackgroundTasks
import requests
from auth.auth_handler import AuthHandler
from db import get_session
from models import UserDefault,User, TokenSchema, UserInput,ChangePasswordRequest
from typing import TypedDict
router = APIRouter()

auth_handler = AuthHandler()


def call_parse_url_api(github_url: str):
    api_url = "http://celery_app:3000/parse-url/"
                
    data = {"url": github_url}
    print('ok')
    try:
        response = requests.post(api_url, json=data)
        if response.status_code != 200:
            print(f"Failed to call parse URL API. Status code: {response.status_code}, Response: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while calling parse URL API: {e}")


@router.post('/signup', summary="Create new user")
async def create_user(user: UserDefault, session=Depends(get_session))-> TypedDict('Response', {"status": int,"data": User}): # type: ignore
    try:
        user_tmp = session.query(User).filter(User.email == user.email).first()
        if user_tmp is None:
            user.password = auth_handler.get_password_hash(user.password)
            user = User.model_validate(user)
            session.add(user)
            session.commit()
            session.refresh(user) 
            if user.github :
                print(user.github)
                call_parse_url_api(user.github)
            return {"status": 200, "data": user}
        else :
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User with this email already exist")
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.post('/login', summary="Create access and refresh tokens for user")
async def login(user: UserInput, session=Depends(get_session)) -> TokenSchema:
    try:
        user_db = session.query(User).filter(User.username == user.username).first()
        if user_db is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect email or password"
            )

        verified = auth_handler.verify_password(user.password, user_db.password)
        if not verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect email or password"
            )

        return {
            "access_token": auth_handler.access_token(user_db.username),
            "refresh_token": auth_handler.refresh_token(user_db.username),
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    
@router.put("/change-password", summary="Change user password")
async def change_password(data: ChangePasswordRequest, current_user: User = Depends(auth_handler.get_current_user), session= Depends(get_session)):
    try:
        user_db = session.query(User).filter(User.username == current_user.username).first()
        if user_db is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User not found"
            )
        
        verified = auth_handler.verify_password(data.old_password, user_db.password)
        if not verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect mail or password"
            )
        

        user_db.password = auth_handler.get_password_hash(data.new_password)
        session.commit()

        return {"message": "Password changed successfully"}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
@router.get('/me', summary='Get details of currently logged in user')
def get_current_user(user: User = Depends(auth_handler.get_current_user)) -> User:
    return user
