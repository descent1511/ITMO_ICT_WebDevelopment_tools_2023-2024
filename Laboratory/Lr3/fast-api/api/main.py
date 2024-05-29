from fastapi import APIRouter
from api.solutions import solutions
from api.users import users
from api.auth import auth
from api.tasks import tasks 
from api.teams import teams
from api.skills import skills
from api.comments import comments
router = APIRouter()

router.include_router(users.router, tags=["users"])
router.include_router(auth.router, tags=["auth"])
router.include_router(tasks.router, tags=["task"])
router.include_router(teams.router, tags=["team"])
router.include_router(skills.router, tags=["skill"])
router.include_router(solutions.router, tags=["solution"])
router.include_router(comments.router, tags=["comment"])