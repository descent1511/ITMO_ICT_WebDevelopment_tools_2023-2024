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
    
