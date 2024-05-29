# API

## Аутентификация (auth)

### Зарегистрироваться   
-   API, используемый для регистрации новых пользователей
-   Метод: `POST`
-   URL : `/signup`
-   Параметры запроса:
    *   user: Объект, содержащий информацию о новом пользователе, включая username и пароль.

### Вход в систему

- API, используемый для создания токенов доступа и обновления для пользователя.
- Метод: `POST`
- URL: `/login`
- Параметры запроса:
    * `user`: Объект, содержащий информацию о пользователе, включая имя пользователя (`username`) и пароль (`password`).

### Изменение пароля пользователя

- API, используемый для изменения пароля пользователя.
- Метод: `PUT`
- URL: `/change-password`
- Параметры запроса:
    * `data`: Объект, содержащий информацию о запросе на изменение пароля, включая старый пароль (`old_password`) и новый пароль (`new_password`).
    * `current_user`: Текущий пользователь, полученный через зависимость `auth_handler.get_current_user()`.

### Получение данных текущего пользователя

- API, используемый для получения информации о текущем вошедшем пользователе.
- Метод: `GET`
- URL: `/me`
- Параметры запроса:
    * `user`: Текущий пользователь, полученный через зависимость `auth_handler.get_current_user()`.

### Код:

```python
from fastapi import Depends, HTTPException, APIRouter,  status
from auth.auth_handler import AuthHandler
from db import get_session
from models import UserDefault,User, TokenSchema, UserInput,ChangePasswordRequest
from typing import TypedDict
router = APIRouter()
auth_handler = AuthHandler()

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

```

## Пользователь (user)

### Установка навыка для пользователей

- API, используемый для назначения навыка пользователю.
- Метод: `POST`
- URL: `/set_skill_for_users/`

- Параметры запроса:
    * `skill_id`: Целочисленное значение, идентификатор навыка.
    * `user_id`: Целочисленное значение, идентификатор пользователя.

### Получение всех пользователей

- API, используемый для получения списка всех пользователей.
- Метод: `GET`
- URL: `/users`

### Удаление пользователя

- API, используемый для удаления пользователя по его идентификатору.
- Метод: `DELETE`
- URL: `/users/{user_id}`

- Параметры запроса:
    * `user_id`: Целочисленное значение, идентификатор пользователя.

### Обновление данных пользователя

- API, используемый для обновления данных пользователя.
- Метод: `PATCH`
- URL: `/users/{user_id}`

- Параметры запроса:
    * `user_id`: Целочисленное значение, идентификатор пользователя.
    * `participant`: Объект, содержащий информацию о пользователе для обновления.

### Код:

```python
from fastapi import Depends, HTTPException, APIRouter,  status
from fastapi.security import OAuth2PasswordRequestForm
from db import get_session
from models import Skill, SkillUserLink, UserDefault,User, UserData
from sqlmodel import  select 
from typing import List, TypedDict
from auth.auth_handler import AuthHandler 
auth_handler = AuthHandler()
router = APIRouter(dependencies=[Depends(auth_handler.get_current_user)],)

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
def update_participant(user_id: int, participant: UserDefault, session=Depends(get_session)) -> TypedDict('Response', {"status": int, "message": str}):  # type: ignore
    try:
        db_participant = session.get(User, user_id)
        if db_participant:
            participant_data = participant.model_dump(exclude_unset=True)
            for key, value in participant_data.items():
                setattr(db_participant, key, value)
            session.add(db_participant)
            session.commit()
            session.refresh(db_participant)
            return {"message": f"Participant with ID {user_id} has been updated successfully."}
        else:
            raise HTTPException(status_code=404, detail=f"Participant with ID {user_id} not found.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## Навыки (Skill)

### Создание навыка

- API, используемый для создания нового навыка.
- Метод: `POST`
- URL: `/skills`
- Параметры запроса:
    * `skill`: Объект, содержащий информацию о новом навыке.

### Получение всех навыков

- API, используемый для получения списка всех навыков.
- Метод: `GET`
- URL: `/skills`

### Получение навыка по ID

- API, используемый для получения информации о навыке по его идентификатору.
- Метод: `GET`
- URL: `/skills/{skill_id}`
- Параметры запроса:
    * `skill_id`: Целочисленное значение, идентификатор навыка.

### Обновление информации о навыке

- API, используемый для обновления информации о навыке.
- Метод: `PATCH`
- URL: `/skills/{skill_id}`
- Параметры запроса:
    * `skill_id`: Целочисленное значение, идентификатор навыка.
    * `skill`: Объект, содержащий информацию о навыке для обновления.

### Удаление навыка

- API, используемый для удаления навыка по его идентификатору.
- Метод: `DELETE`
- URL: `/skills/{skill_id}`
- Параметры запроса:
    * `skill_id`: Целочисленное значение, идентификатор навыка.

### Код:
```python 
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

```

## Команда (Team)

### Создание команды

- API, используемый для создания новой команды.
- Метод: `POST`
- URL: `/teams`
- Параметры запроса:
    * `team`: Объект, содержащий информацию о новой команде.

### Получение всех команд

- API, используемый для получения списка всех команд.
- Метод: `GET`
- URL: `/teams`

### Обновление информации о команде

- API, используемый для обновления информации о команде.
- Метод: `PATCH`
- URL: `/teams/{team_id}`

- Параметры запроса:
    * `team_id`: Целочисленное значение, идентификатор команды.
    * `team`: Объект, содержащий информацию о команде для обновления.

### Удаление команды

- API, используемый для удаления команды по ее идентификатору.
- Метод: `DELETE`
- URL: `/teams/{team_id}`
- Параметры запроса:
    * `team_id`: Целочисленное значение, идентификатор команды.

### Присоединение к команде

- API, используемый для присоединения к команде.
- Метод: `POST`
- URL: `/memberships`
- Параметры запроса:
    * `membership`: Объект, содержащий информацию о членстве в команде.

### Код:
```python 
from fastapi import APIRouter, Depends, HTTPException
from db import get_session
from models import Team, TeamDefault, MemberShip,TeamCreateRequest,User,TeamData
from sqlmodel import  select 
from typing import List, TypedDict
from auth.auth_handler import AuthHandler 
auth_handler = AuthHandler()
router = APIRouter(dependencies=[Depends(auth_handler.get_current_user)],)

@router.post("/teams")
def create_team(team: TeamCreateRequest,session=Depends(get_session)) -> TypedDict('Response', {"status": int, "message": str}):  # type: ignore
   
    try:
        user_id = team.user_id
        team = Team.model_validate(TeamDefault(name=team.name))

        if team: 
            session.add(team)
            session.commit()
            session.refresh(team)

            membership = MemberShip(team_id=team.id, user_id=user_id, request_status="created")
            session.add(membership)
            session.commit()
            session.refresh(membership) 

        return {"status": 200, "message": f"Participant with ID {user_id} has successfully created a team."}
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/teams")
def get_all_teams(session=Depends(get_session)) -> List[TeamData]:
    try:
        query = select(Team)
        return session.exec(query).all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/teams/{team_id}")
def update_team(team_id: int, team: TeamDefault, session=Depends(get_session)) -> TypedDict('Response', {"status": int, "message": str}):  # type: ignore
    try:
        db_team = session.get(Team, team_id)
        if db_team:
            team_data = team.model_dump(exclude_unset=True)
            for key, value in team_data.items():
                setattr(db_team, key, value)
            session.add(db_team)
            session.commit()
            session.refresh(db_team)
            return {"message": f"Team with ID {team_id} has been updated successfully."}
        else:
            raise HTTPException(status_code=404, detail=f"Team with ID {team_id} not found.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.delete("/teams/{team_id}")
def delete_team(team_id: int, session=Depends(get_session)) -> TypedDict('Response', {"status": int, "message": str}):  # type: ignore
    try:
        team = session.get(Team, team_id)
        if team:
            session.delete(team)
            session.commit()
            return {"status": 200, "message": f"Team with ID {team_id} has been deleted successfully."}
        else:
            raise HTTPException(status_code=404, detail=f"Team with ID {team_id} not found.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/memberships")
def join_team(membership: MemberShip, session=Depends(get_session)) -> TypedDict('Response', {"status": int, "message": str}): # type: ignore
    try:
        participant = session.get(User, membership.user_id)
        if not participant:
            raise HTTPException(status_code=404, detail=f"Participant with id {membership.user_id} not found")
        
        team = session.get(Team, membership.team_id)
        if not team:
            raise HTTPException(status_code=404, detail=f"Team with id {membership.team_id} not found")
        
        membership = MemberShip.model_validate(membership)
        session.add(membership)
        session.commit()
        session.refresh(membership)
        
        return {"status": 200, "message": f"Participant with ID {membership.user_id} has successfully sent invitation to join team with ID {membership.team_id}."}
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    
```
## Решение

### Создание решения

- API, используемый для создания нового решения.
- Метод: `POST`
- URL: `/solutions`
- Параметры запроса:
    * `solution`: Объект, содержащий информацию о новом решении.

### Получение всех решений

- API, используемый для получения списка всех решений.
- Метод: `GET`
- URL: `/solutions`


### Получение решения по ID

- API, используемый для получения информации о решении по его идентификатору.
- Метод: `GET`
- URL: `/solutions/{solution_id}`
- Параметры запроса:
    * `solution_id`: Целочисленное значение, идентификатор решения.

### Обновление информации о решении

- API, используемый для обновления информации о решении.
- Метод: `PATCH`
- URL: `/solutions/{solution_id}`
- Параметры запроса:
    * `solution_id`: Целочисленное значение, идентификатор решения.
    * `solution`: Объект, содержащий информацию о решении для обновления.

### Удаление решения

- API, используемый для удаления решения по его идентификатору.
- Метод: `DELETE`
- URL: `/solutions/{solution_id}`
- Параметры запроса:
    * `solution_id`: Целочисленное значение, идентификатор решения.

### Код:
```python 
from fastapi import Depends, HTTPException, APIRouter

from db import get_session
from models import Solution, SolutionDefault,SolutionData
from typing import List, TypedDict
from auth.auth_handler import AuthHandler 
auth_handler = AuthHandler()
router = APIRouter(dependencies=[Depends(auth_handler.get_current_user)],)
@router.post("/solutions")
def create_solution(solution: SolutionDefault, session=Depends(get_session)) -> TypedDict('Response', {"status": int, "message": str}): # type: ignore
    try:
        solution = Solution.model_validate(solution)
        session.add(solution)
        session.commit()
        session.refresh(solution)
        return {"status": 200, "message": f"Solution of the team with ID {solution.team_id} has been created successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/solutions")
def get_all_solutions(session=Depends(get_session)) -> List[SolutionData]:
    try:
        solutions = session.query(Solution).all()
        return solutions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/solutions/{solution_id}")
def get_solution(solution_id: int, session=Depends(get_session)) -> SolutionData: # type: ignore
    try:
        solution = session.get(Solution, solution_id)
        if solution:
            return solution
        else:
            raise HTTPException(status_code=404, detail=f"Solution with ID {solution_id} not found.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/solutions/{solution_id}")
def update_solution(solution_id: int, solution: SolutionDefault, session=Depends(get_session)) -> TypedDict('Response', {"status": int, "message": str}):  # type: ignore
    try:
        db_solution = session.get(Solution, solution_id)
        if db_solution:
            solution_data = solution.model_dump(exclude_unset=True)
            for key, value in solution_data.items():
                setattr(db_solution, key, value)
            session.add(db_solution)
            session.commit()
            session.refresh(db_solution)
            return {"status": 200, "message": f"Solution with ID {solution_id} has been updated successfully."}
        else:
            raise HTTPException(status_code=404, detail=f"Solution with ID {solution_id} not found.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/solutions/{solution_id}")
def delete_solution(solution_id: int, session=Depends(get_session)):
    try:
        solution = session.get(Solution, solution_id)
        if solution:
            session.delete(solution)
            session.commit()
            return {"message": f"Solution with ID {solution_id} has been deleted successfully."}
        else:
            raise HTTPException(status_code=404, detail=f"Solution with ID {solution_id} not found.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## Задача

### Создание задачи

- API, используемый для создания новой задачи.
- Метод: `POST`
- URL: `/tasks`
- Параметры запроса:
    * `user_id`: Целочисленное значение, идентификатор пользователя, создающего задачу.
    * `task`: Объект, содержащий информацию о новой задаче.

### Получение всех задач

- API, используемый для получения списка всех задач.
- Метод: `GET`
- URL: `/tasks`

### Удаление задачи

- API, используемый для удаления задачи по ее идентификатору.
- Метод: `DELETE`
- URL: `/tasks/{task_id}`
- Параметры запроса:
    * `task_id`: Целочисленное значение, идентификатор задачи.

### Обновление информации о задаче

- API, используемый для обновления информации о задаче.
- Метод: `PATCH`
- URL: `/tasks/{task_id}`
- Параметры запроса:
    * `task_id`: Целочисленное значение, идентификатор задачи.
    * `task`: Объект

### Код:
```python 
from fastapi import Depends, HTTPException,APIRouter
from db import get_session
from models import User, Role, Task, TaskDefault
from sqlmodel import  select 
from typing import List, TypedDict

from auth.auth_handler import AuthHandler 
auth_handler = AuthHandler()
router = APIRouter(dependencies=[Depends(auth_handler.get_current_user)],)

@router.post("/tasks")
def create_task(user_id: int, task: TaskDefault, session=Depends(get_session))-> TypedDict('Response', {"status": int, "message": str}): # type: ignore
    try:
        participant = session.get(User,user_id)
        if participant.role == Role.admin :
            task = Task.model_validate(task)
            session.add(task)
            session.commit()
            session.refresh(task)
            return {"status": 200, "message": "Task created successfully."}
        else:
            raise HTTPException(status_code=403, detail="Only admins can create tasks.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tasks")
def get_all_tasks(session=Depends(get_session)) -> List[Task] :
    try:
        query = select(Task)
        return session.exec(query).all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/tasks/{task_id}")
def delete_task(task_id: int, user_id: int, session=Depends(get_session)) -> TypedDict('Response', {"status": int, "message": str}): # type: ignore
    try:
        participant = session.get(User, user_id)
        if not participant or participant.role != Role.admin:
            raise HTTPException(status_code=403, detail="Only admins can delete tasks.")
        

        db_task = session.get(Task, task_id)
        
        if db_task:
            session.delete(db_task)
            session.commit()
            return {"status": 200, "message": f"Task with ID {task_id} has been deleted successfully."}
        else:
            raise HTTPException(status_code=404, detail=f"Task with ID {task_id} not found.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.patch("/tasks/{task_id}")
def update_task(task_id: int,user_id: int, task: TaskDefault, session=Depends(get_session)) -> TypedDict('Response', {"status": int, "message": str}): # type: ignore
    try:
        participant = session.get(User, user_id)
        if not participant or participant.role != Role.admin:
            raise HTTPException(status_code=403, detail="Only admins can update tasks.")
    
        db_task = session.get(Task, task_id)
        
        if db_task:
            task = task.model_dump(exclude_unset=True)
            for key, value in task.items():
               setattr(db_task, key, value)
            session.add(db_task)
            session.commit()
            session.refresh(db_task)
            return {"status": 200, "message": f"Task with ID {task_id} has been updated successfully."}
        else:
            raise HTTPException(status_code=404, detail=f"Task with ID {task_id} not found.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## Комментарий

### Создание комментария

- API, используемый для создания нового комментария.
- Метод: `POST`
- URL: `/comments`
- Параметры запроса:
    * `comment`: Объект, содержащий информацию о новом комментарии.

### Получение всех комментариев

- API, используемый для получения списка всех комментариев.
- Метод: `GET`
- URL: `/comments`

### Получение комментария по его ID

- API, используемый для получения комментария по его идентификатору.
- Метод: `GET`
- URL: `/comments/{comment_id}`
- Параметры запроса:
    * `comment_id`: Целочисленное значение, идентификатор комментария.

### Обновление информации о комментарии

- API, используемый для обновления информации о комментарии.
- Метод: `PATCH`
- URL: `/comments/{comment_id}`
- Параметры запроса:
    * `comment_id`: Целочисленное значение, идентификатор комментария.
    * `comment`: Объект, содержащий обновленную информацию о комментарии.

### Удаление комментария

- API, используемый для удаления комментария по его идентификатору.
- Метод: `DELETE`
- URL: `/comments/{comment_id}`
- Параметры запроса:
    * `comment_id`: Целочисленное значение, идентификатор комментария.

### Код:
```python
from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy.orm import Session
from typing import List, TypedDict
from db import get_session
from models import Comment, CommentDefault

from auth.auth_handler import AuthHandler 
auth_handler = AuthHandler()
router = APIRouter(dependencies=[Depends(auth_handler.get_current_user)],)

@router.post("/comments")
def create_comment(comment: CommentDefault, session = Depends(get_session)) -> TypedDict('Response', {"status": int, "message": str}): # type: ignore
    try:
        comment = Comment.model_validate(comment)
        session.add(comment)
        session.commit()
        session.refresh(comment)
        return {"status": 200, "message": "Comment has been created successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/comments")
def get_all_comments(session= Depends(get_session)) -> List[Comment]:
    try:
        comments = session.query(Comment).all()
        return comments
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/comments/{comment_id}", response_model=Comment)
def get_comment(comment_id: int, session = Depends(get_session)):
    try:
        comment = session.query(Comment).filter(Comment.id == comment_id).first()
        if comment:
            return comment
        else:
            raise HTTPException(status_code=404, detail=f"Comment with ID {comment_id} not found.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/comments/{comment_id}")
def update_comment(comment_id: int, comment: CommentDefault, session: Session = Depends(get_session))-> TypedDict('Response', {"status": int, "message": str}): # type: ignore
    try:
        db_comment = session.query(Comment).filter(Comment.id == comment_id).first()
        if db_comment:
            comment_data = comment.model_dump(exclude_unset=True)
            for key, value in comment_data.items():
                setattr(db_comment, key, value)
            session.commit()
            session.refresh(db_comment)
            return db_comment
        else:
            raise {"status": 200, "message": f"Comment with ID {skill_id} has been updated successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/comments/{comment_id}")
def delete_comment(comment_id: int, session: Session = Depends(get_session)) -> TypedDict('Response', {"status": int, "message": str}): # type: ignore
    try:
        comment = session.query(Comment).filter(Comment.id == comment_id).first()
        if comment:
            session.delete(comment)
            session.commit()
            return {"status": 200, "message": f"Comment with ID {comment_id} has been deleted successfully."}
        else:
            raise HTTPException(status_code=404, detail=f"Comment with ID {comment_id} not found.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

```
