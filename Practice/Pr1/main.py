from fastapi import FastAPI
from enum import Enum
from typing import Optional, List, TypedDict
from models import Warrior, RaceType, Profession, Skill
from pydantic import BaseModel

app = FastAPI()

temp_bd = [
    {
        "id": 1,
        "race": "director",
        "name": "Мартынов Дмитрий",
        "level": 12,
        "profession": {
            "id": 1,
            "title": "Влиятельный человек",
            "description": "Эксперт по всем вопросам"
        },
        "skills":
        [{
            "id": 1,
            "name": "Купле-продажа компрессоров",
            "description": ""

        },
            {
            "id": 2,
            "name": "Оценка имущества",
            "description": ""

        }]
    },
    {
        "id": 2,
        "race": "worker",
        "name": "Андрей Косякин",
        "level": 12,
        "profession": {
            "id": 1,
            "title": "Дельфист-гребец",
            "description": "Уважаемый сотрудник"
        },
        "skills": []
    },
]

temp_professions_db = [
    {"id": 1, "title": "Влиятельный человек",
        "description": "Эксперт по всем вопросам"},
    {"id": 2, "title": "Дельфист-гребец", "description": "Уважаемый сотрудник"}
]


@app.get("/warriors_list")
def warriors_list() -> List[Warrior]:
    return temp_bd


@app.get("/warrior/{warrior_id}")
def warriors_get(warrior_id: int) -> List[Warrior]:
    return [warrior for warrior in temp_bd if warrior.get("id") == warrior_id]


@app.post("/warrior")
def warriors_create(warrior: Warrior) -> TypedDict('Response', {"status": int, "data": Warrior}):
    warrior_to_append = warrior.model_dump()
    temp_bd.append(warrior_to_append)
    return {"status": 200, "data": warrior}


@app.delete("/warrior/delete{warrior_id}")
def warrior_delete(warrior_id: int):
    for i, warrior in enumerate(temp_bd):
        if warrior.get("id") == warrior_id:
            temp_bd.pop(i)
            break
    return {"status": 201, "message": "deleted"}


@app.put("/warrior{warrior_id}")
def warrior_update(warrior_id: int, warrior: Warrior) -> List[Warrior]:
    for war in temp_bd:
        if war.get("id") == warrior_id:
            warrior_to_append = warrior.model_dump()
            temp_bd.remove(war)
            temp_bd.append(warrior_to_append)
    return temp_bd


@app.get("/professions")
def get_professions() -> List[Profession]:
    return temp_professions_db


@app.get("/profession/{profession_id}")
def get_profession(profession_id: int) -> Profession:
    for profession in temp_professions_db:
        if profession["id"] == profession_id:
            return profession


@app.post("/profession")
def create_profession(profession: Profession) -> TypedDict('Response', {"status": int, "data": Profession}):
    profession_data = profession.model_dump()
    temp_professions_db.append(profession_data)
    return profession_data


@app.put("/profession/{profession_id}", response_model=Profession)
def update_profession(profession_id: int, profession: Profession) -> Profession:
    for i, prof in enumerate(temp_professions_db):
        if prof["id"] == profession_id:
            temp_professions_db[i] = profession.model_dump()
            temp_professions_db[i]["id"] = profession_id
            return temp_professions_db[i]


@app.delete("/profession/{profession_id}")
def delete_profession(profession_id: int):
    for i, profession in enumerate(temp_professions_db):
        if profession["id"] == profession_id:
            temp_professions_db.pop(i)
            return {"status": "success", "message": "Profession deleted"}
