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
