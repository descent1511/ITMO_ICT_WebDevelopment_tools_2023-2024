from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy.orm import Session

from typing import List, TypedDict
from db import get_session
from models import Skill, SkillDefault

from auth.auth_handler import AuthHandler 
auth_handler = AuthHandler()
router = APIRouter(dependencies=[Depends(auth_handler.get_current_user)],)


@router.post("/skills")
def create_skill(skill: SkillDefault, session=Depends(get_session))-> TypedDict('Response', {"status": int, "message": str}): # type: ignore
    try:
        skill = Skill.model_validate(skill)
        session.add(skill)
        session.commit()
        session.refresh(skill)
        return {"status": 200, "message": f"Skill has been created successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/skills")
def get_all_skills(session=Depends(get_session)) -> List[Skill]:
    try:
        skills = session.query(Skill).all()
        return skills
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/skills/{skill_id}")
def get_skill(skill_id: int, session=Depends(get_session)) -> Skill:
    try:
        skill = session.query(Skill).filter(Skill.id == skill_id).first()
        if skill:
            return skill
        else:
            raise HTTPException(status_code=404, detail=f"Skill with ID {skill_id} not found.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/skills/{skill_id}")
def update_skill(skill_id: int, skill: SkillDefault, session=Depends(get_session)) -> TypedDict('Response', {"status": int, "message": str}): # type: ignore
    try:
        db_skill = session.query(Skill).filter(Skill.id == skill_id).first()
        if db_skill:
            skill_data = skill.model_dump(exclude_unset=True)
            for key, value in skill_data.items():
                setattr(db_skill, key, value)
            session.commit()
            session.refresh(db_skill)
            return db_skill
        else:
            return {"status": 200, "message": f"Skill with ID {skill_id} has been updated successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/skills/{skill_id}")
def delete_skill(skill_id: int, session=Depends(get_session)):
    try:
        skill = session.query(Skill).filter(Skill.id == skill_id).first()
        if skill:
            session.delete(skill)
            session.commit()
            return {"message": f"Skill with ID {skill_id} has been deleted successfully."}
        else:
            raise HTTPException(status_code=404, detail=f"Skill with ID {skill_id} not found.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
