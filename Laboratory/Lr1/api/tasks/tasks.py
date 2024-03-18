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