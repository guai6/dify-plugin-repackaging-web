from fastapi import APIRouter
from .tasks import router as tasks_router
from .files import router as files_router
from .system import router as system_router

main_router = APIRouter()

main_router.include_router(tasks_router, prefix="/tasks", tags=["tasks"])
main_router.include_router(files_router, prefix="/files", tags=["files"])
main_router.include_router(system_router, prefix="/system", tags=["system"])