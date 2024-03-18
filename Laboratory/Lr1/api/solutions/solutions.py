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