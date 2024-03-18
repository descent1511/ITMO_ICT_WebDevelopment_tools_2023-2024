# Модель данных

## Перечисления (Enum):
### Пол (Gender):  
Определяет перечисление для пола пользователя в системе. 

- `male` - Мужской
- `female` - Женский

### Роль (Role): 
Определяет перечисление для ролей пользователя, включая администратора, участника и экзаменатора.

- `admin` - Администратор
- `participant` - Участник
- `examiner` - Экзаменатор

### Статус запроса (RequestStatus): 
Определяет состояние запроса, включая ожидание, принято, отклонено, отменено и создано.

- `pending` - В ожидании
- `accepted` - Принят
- `rejected` - Отклонён
- `cancelled` - Отменён
- `created` - Создан

## Классы моделей:

### Связь между пользователем и навыком (SkillUserLink): 
Таблица связи между пользователем и навыком, позволяющая управлять отношениями между этими сущностями.

- `skill_id` - ID навыка
- `user_id` - ID пользователя

### Членство в команде (MemberShip): 
Сохраняет информацию о присоединении пользователя к команде, включая статус запроса и сообщение запроса.

- `team_id` - ID команды
- `user_id` - ID пользователя
- `request_status` - Статус запроса
- `request_message` - Сообщение запроса

### Навык (Skill): 
Определяет подробную информацию о навыке, включая идентификатор, название, описание и список связанных пользователей.

- `id` - ID
- `name` - Название
- `description` - Описание
- `users` - Пользователи, связанные с этим навыком

### Команда (Team): 
Определяет подробную информацию о команде, включая идентификатор, название, дату создания и список участников и решений команды.

- `id` - ID
- `name` - Название
- `creation_date` - Дата создания
- `users` - Пользователи, состоящие в этой команде
- `solutions` - Решения, связанные с этой командой

### Пользователь (User): 
Определяет подробную информацию о пользователе, включая идентификатор, информацию о пользователе, список навыков и список команд, в которых участвует пользователь

- `id` - ID
- `name` - Имя
- `username` - Имя пользователя
- `password` - Пароль
- `email` - Электронная почта
- `telephone` - Телефон
- `registration_date` - Дата регистрации
- `status` - Статус
- `role` - Роль
- `gender` - Пол
- `skills` - Навыки, связанные с этим пользователем
- `teams` - Команды, в которых состоит этот пользователь

### Задача (Task): 
Определяет подробную информацию о задаче, включая идентификатор, информацию о задаче и список решений для этой задачи.

- `id` - ID
- `name` - Название
- `description` - Описание
- `requirements` - Требования
- `evaluation_criteria` - Критерии оценки
- `publish_date` - Дата публикации
- `solutions` - Решения, связанные с этой задачей

### Решение (Solution): 
Определяет подробную информацию о решении, включая идентификатор, содержание, дату представления, команду и задачу, связанные с этим решением, а также список комментариев.

- `id` - ID
- `content` - Содержание
- `submission_date` - Дата подачи
- `team_id` - ID команды
- `task_id` - ID задачи
- `team` - Команда, связанная с этим решением
- `task` - Задача, связанная с этим решением

### Комментарий (Comment): 
Определяет подробную информацию о комментарии, включая идентификатор, содержание, дату создания, пользователя и решение, связанные с этим комментарием.

- `id` - ID
- `content` - Содержание
- `creation_date` - Дата создания
- `solution_id` - ID решения
- `user_id` - ID пользователя
- `user` - Пользователь, связанный с этим комментарием
- `solution` - Решение, связанное с этим комментарием


## Код:
```python
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
    name: str
    username : str 
    password : str 
    email: str
    telephone : str
    registration_date : datetime = datetime.now()
    status: Optional[bool] = Field(default=False)
    role: Role = Field(default=Role.participant)
    gender : Gender

    @field_validator("email")
    @classmethod
    def validate_email(cls, value):
        try:
            validate_email(value)
        except EmailNotValidError:
            raise ValueError("Invalid email format")
        return value

class User(UserDefault,table=True):
    id: int = Field(default=None, primary_key=True)
    skills: Optional[List[Skill]] = Relationship(
        back_populates="users", link_model=SkillUserLink)
    teams : Optional[List[Team]] = Relationship(
        back_populates="users", link_model=MemberShip)
    comments:  Optional[List["Comment"]] = Relationship(back_populates="user")
    
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
    users: Optional[List["User"]] = None
    solutions : Optional[List["Solution"]]  = None
class UserData(UserDefault) :
    skills: Optional[List[Skill]] = None
    teams : Optional[List[Team]] = None

class SolutionData(SolutionDefault) :
    team: Optional[Team] = None
    task : Optional[Task] = None

class TaskData(TaskDefault) :
    
    solutions : Optional[List["Solution"]] = None
```
