from enum import Enum
from typing import Optional, List


from pydantic import BaseModel

class RaceType(Enum):
    director = "director"
    worker = "worker"
    junior = "junior"

class Profession(BaseModel):
    id: int
    title: str
    description: str

class Skill(BaseModel):
    id: int
    name: str
    description: str

class Warrior(BaseModel):
    id: int
    race: RaceType
    name: str
    level: int
    profession: Profession
    skills: Optional[List[Skill]] = []

