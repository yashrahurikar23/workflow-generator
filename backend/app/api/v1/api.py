from app.api.v1.endpoints import chat, visual_workflows, workflows
from fastapi import APIRouter

api_router = APIRouter()

api_router.include_router(workflows.router, prefix="/workflows", tags=["workflows"])
api_router.include_router(visual_workflows.router, prefix="/visual", tags=["visual-workflows"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
