from .recipes import router as recipe_router
from fastapi import APIRouter


api_router = APIRouter(prefix="/api")
api_router.include_router(recipe_router)
