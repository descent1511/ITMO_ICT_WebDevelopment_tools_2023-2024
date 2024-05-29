from fastapi import Depends, HTTPException, APIRouter,  status
from fastapi.security import OAuth2PasswordRequestForm
from db import get_session
from models import Skill, SkillUserLink, UserDefault,User, UserData, UserUpdate
from sqlmodel import  select 
from typing import List, TypedDict
from auth.auth_handler import AuthHandler
auth_handler = AuthHandler()
router = APIRouter()

@router.post("/set_skill_for_users/")
def set_skill_for_users(skill_id: int, user_id: int, session = Depends(get_session)) -> TypedDict('Response', {"status": int, "message": str}):  # type: ignore
    try:
        skill = session.query(Skill).filter(Skill.id == skill_id).first()
        if skill is None:
            raise HTTPException(status_code=404, detail="Skill not found")

        user = session.query(User).filter(User.id == user_id).first()
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        skill_user_link = SkillUserLink(skill_id=skill_id, user_id=user_id)
        session.add(skill_user_link)
        session.commit()
        return {"status": 200, "message": "Skill assigned to user successfully."}
    except Exception as e:
        
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/users")
def get_all_users(session=Depends(get_session)) -> List[UserData]:
    try:
        query = select(User)
        return session.exec(query).all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/users/{user_id}")
def delete_participant(user_id: int, session=Depends(get_session)) -> TypedDict('Response', {"status": int, "message": str}):  # type: ignore
    try:
        user = session.get(User, user_id)
        if user:
            session.delete(user)
            session.commit()
            return {"status": 200, "message": f"Participant with ID {user_id} has been deleted successfully."}
        else:
            raise HTTPException(status_code=404, detail=f"Participant with ID {user_id} not found.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/users/{user_id}")
def update_participant(user_id: int, participant: UserUpdate, session=Depends(get_session)) -> TypedDict('Response', {"status": int, "message": str}):  # type: ignore
    try:
        db_participant = session.get(User, user_id)
        if db_participant:
            participant_data = participant.model_dump(exclude_unset=True)
            for key, value in participant_data.items():
                if value :
                    setattr(db_participant, key, value)
            session.add(db_participant)
            session.commit()
            session.refresh(db_participant)
            return {"status": 200, "message": f"Participant with ID {user_id} has been updated successfully."}
        else:
            raise HTTPException(status_code=404, detail=f"Participant with ID {user_id} not found.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/users/github")
def get_user_by_github(github: str, session = Depends(get_session)) -> UserData:
    try:
        user = session.query(User).filter(User.github == github).first()
        if user:
            return user
        else:
            raise HTTPException(status_code=404, detail=f"User with GitHub username '{github}' not found.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))