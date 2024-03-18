
from fastapi import Depends, FastAPI, HTTPException
from db import init_db,get_session
from contextlib import asynccontextmanager
from models import WarriorDefault, Warrior,Profession,ProfessionDefault,WarriorData,SkillDefault,Skill,SkillWarriorLink
from typing import Optional, List, TypedDict
from sqlmodel import  select
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    get_session()
    yield

app = FastAPI(lifespan=lifespan)


@app.post("/warrior")
def warriors_create(warrior: WarriorDefault, session=Depends(get_session)) -> TypedDict('Response', {"status": int,"data": Warrior}):  # type: ignore
    warrior = Warrior.model_validate(warrior)
    session.add(warrior)
    session.commit()
    session.refresh(warrior)
    return {"status": 200, "data": warrior}

@app.get("/warriors_list")
def warriors_list(session=Depends(get_session)) -> List[Warrior]:
    return session.exec(select(Warrior)).all()


# @app.get("/warrior/{warrior_id}")
# def warriors_get(warrior_id: int, session=Depends(get_session)) -> Warrior:
#     return session.exec(select(Warrior).where(Warrior.id == warrior_id)).first()

@app.get("/warrior/{warrior_id}")
def warriors_get(warrior_id: int, session=Depends(get_session)) -> WarriorData:
    warrior = session.get(Warrior, warrior_id)
    return warrior

@app.patch("/warrior/{warrior_id}")
def warrior_update(warrior_id: int, warrior: WarriorDefault, session=Depends(get_session)) -> WarriorDefault:
    db_warrior = session.get(Warrior, warrior_id)
    if not db_warrior:
        raise HTTPException(status_code=404, detail="Warrior not found")
    warrior_data = warrior.model_dump(exclude_unset=True)
    for key, value in warrior_data.items():
        setattr(db_warrior, key, value)
    session.add(db_warrior)
    session.commit()
    session.refresh(db_warrior)
    return db_warrior

@app.get("/professions_list")
def professions_list(session=Depends(get_session)) -> List[Profession]:
    return session.exec(select(Profession)).all()


@app.get("/profession/{profession_id}")
def profession_get(profession_id: int, session=Depends(get_session)) -> Profession:
    return session.get(Profession, profession_id)


@app.post("/profession")
def profession_create(prof: ProfessionDefault, session=Depends(get_session)) -> TypedDict('Response', {"status": int, "data": Profession}): # type: ignore
    prof = Profession.model_validate(prof)
    session.add(prof)
    session.commit()
    session.refresh(prof)
    return {"status": 200, "data": prof}

@app.delete("/warrior/delete{warrior_id}")
def warrior_delete(warrior_id: int, session=Depends(get_session)):
    warrior = session.get(Warrior, warrior_id)
    if not warrior:
        raise HTTPException(status_code=404, detail="Warrior not found")
    session.delete(warrior)
    session.commit()
    return {"ok": True}



@app.post("/profession")
def profession_create(prof: ProfessionDefault, session=Depends(get_session)) -> TypedDict('Response', {"status": int, "data": Profession}): # type: ignore
    prof = Profession.model_validate(prof)
    session.add(prof)
    session.commit()
    session.refresh(prof)
    return {"status": 200, "data": prof}

@app.post("/skill/")
def create_skill(skill: SkillDefault, session=Depends(get_session)) -> TypedDict('Response', {"status": int, "data": Skill}): # type: ignore
    skill = Skill.model_validate(skill)
    session.add(skill)
    session.commit()
    session.refresh(skill)
    return {"status": 200, "data": skill}

@app.get("/skills/")
def get_skills(session=Depends(get_session))->  List[Skill]:
    return session.exec(select(Skill)).all()

@app.get("/skill/{skill_id}")
def get_skill(skill_id: int, session=Depends(get_session))->Skill:
    return session.get(Skill, skill_id)

@app.put("/skill/{skill_id}")
def update_skill(skill_id: int, skill: SkillDefault, session=Depends(get_session))->SkillDefault:
    skill = session.get(Skill, skill_id)
    if skill is None:
        raise HTTPException(status_code=404, detail="Skill not found")
    
    skill_data = skill.model_dump(exclude_unset=True)
    for key, value in skill_data.items():
        setattr(skill, key, value)
    session.add(skill)
    session.commit()
    session.refresh(skill)
    return skill

@app.delete("/skill/{skill_id}")
def delete_skill(skill_id: int, session=Depends(get_session)):
    skill = session.get(Skill, skill_id)
    if skill is None:
        raise HTTPException(status_code=404, detail="Skill not found")
    session.delete(skill)
    session.commit()
    return {"message": "Skill deleted successfully"}


@app.post("/skilluser")
def create_skill_warrior_link(su: SkillWarriorLink, session=Depends(get_session)) -> TypedDict('Response', {"status": int,"data": SkillWarriorLink}): 
    warrior = SkillWarriorLink.model_validate(su)
    session.add(su)
    session.commit()
    session.refresh(su)
    return {"status": 200, "data": su}