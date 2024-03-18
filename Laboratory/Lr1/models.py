from typing import Optional, List
from email_validator import EmailNotValidError
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime, time, timedelta
from enum import Enum
from pydantic import EmailStr, field_validator, validate_email
class Gender(Enum):
    male = "male"
    female = "female"

class Role(Enum) :
    admin = "admin"
    participant = "participant"
    examiner = "examiner"

class TokenSchema(SQLModel):
    access_token: str
    refresh_token: str

class TokenPayload(SQLModel):
    sub: int = None
    exp: int = None


class UserInput(SQLModel):
    username: str
    password: str

class RequestStatus(Enum):
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"
    cancelled = "cancelled"
    created = "created"

class SkillUserLink(SQLModel, table=True):
    skill_id: Optional[int] = Field(
        default=None, foreign_key="skill.id", primary_key=True
    )
    user_id: Optional[int] = Field(
        default=None, foreign_key="user.id", primary_key=True
    )
   

class MemberShip(SQLModel, table=True) :
    team_id: Optional[int] = Field(
        default=None, foreign_key="team.id", primary_key=True
    )
    user_id: Optional[int] = Field(
        default=None, foreign_key="user.id", primary_key=True
    )
    request_status: Optional[str] = Field(default=RequestStatus.pending)  
    request_message: Optional[str] = None

class SkillDefault(SQLModel):
    name: str
    description: Optional[str] = ""


class Skill(SkillDefault, table=True):
    id: int = Field(default=None, primary_key=True)
    users: Optional[List["User"]] = Relationship(
        back_populates="skills", link_model=SkillUserLink)

class ChangePasswordRequest(SQLModel):
    old_password: str
    new_password: str

class TeamCreateRequest(SQLModel):
    name: str
    user_id: int

class TeamDefault(SQLModel) :
    name : str
    creation_date : datetime = datetime.now()

class Team(TeamDefault,table = True) :
    id: int = Field(default=None, primary_key=True)
    users: Optional[List["User"]] = Relationship(
        back_populates="teams", link_model=MemberShip)
    solutions : Optional[List["Solution"]]  = Relationship(back_populates="team")

class UserDefault(SQLModel) :
    name: Optional[str]
    username : Optional[str]
    password : Optional[str] 
    email: Optional[str]
    telephone : Optional[str]
    registration_date : Optional[datetime] = datetime.now()
    status: Optional[bool] = Field(default=False)
    role: Optional[Role] = Field(default=Role.participant)
    gender : Optional[Gender]

    @field_validator("email")
    @classmethod
    def validate_email(cls, value):
        try:
            validate_email(value)
        except EmailNotValidError:
            raise ValueError("Invalid email format")
        return value
    
class UserUpdate(SQLModel):
    name: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    email: Optional[EmailStr] = None
    telephone: Optional[str] = None
    registration_date: Optional[datetime] = None
    status: Optional[bool] = None
    role: Optional[Role] = None
    gender: Optional[Gender] = None

class User(UserDefault,table=True):
    id: int = Field(default=None, primary_key=True)
    skills: Optional[List[Skill]] = Relationship(
        back_populates="users", link_model=SkillUserLink)
    teams : Optional[List[Team]] = Relationship(
        back_populates="users", link_model=MemberShip)
    comments:  Optional[List["Comment"]] = Relationship(back_populates="user")

class UpdateUser(SQLModel):
    name: Optional[str]
    telephone: Optional[str]
    gender: Optional[str]


class TaskCreateRequest(SQLModel):
    user_id: int
    name : str
    description : str
    requirements : str
    evaluation_criteria : str
    publish_date : datetime  = datetime.now()

class TaskDefault(SQLModel) :
    name : str
    description : str
    requirements : str
    evaluation_criteria : str
    publish_date : datetime  = datetime.now()

class Task(TaskDefault,table = True) :
    id: int = Field(default=None, primary_key=True)
    solutions : Optional[List["Solution"]] = Relationship(back_populates="task")

class SolutionDefault(SQLModel) :
    content : Optional[str] 
    submission_date : datetime =  datetime.now()
    team_id: Optional[int] = Field(default=None, foreign_key="team.id")
    task_id: Optional[int] = Field(default=None, foreign_key="task.id")

class Solution(SolutionDefault,table = True) :
    id: int = Field(default=None, primary_key=True)
    team: Optional[Team] = Relationship(back_populates="solutions")
    task : Optional[Task] = Relationship(back_populates="solutions")
    comments:  Optional[List["Comment"]] = Relationship(back_populates="solution")

class CommentDefault(SQLModel) :
    content : Optional[str] 
    creation_date : datetime = datetime.now()
    solution_id: Optional[int] = Field(default=None, foreign_key="solution.id")
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")

class Comment(CommentDefault, table = True) :
    id: int = Field(default=None, primary_key=True)
    user: Optional[User] = Relationship(back_populates="comments")
    solution : Optional[Solution]  = Relationship(back_populates="comments")

class TeamData(TeamDefault) :
    id : int 
    users: Optional[List["User"]] = None
    solutions : Optional[List["Solution"]]  = None
class UserData(UserDefault) :
    id : int 
    skills: Optional[List[Skill]] = None
    teams : Optional[List[Team]] = None

class SolutionData(SolutionDefault) :
    id : int 
    team: Optional[Team] = None
    task : Optional[Task] = None

class TaskData(TaskDefault) :
    id : int 
    solutions : Optional[List["Solution"]] = None