"""
API routes package.
"""
from fastapi import APIRouter

from backend.api.routes.devices import router as devices_router
from backend.api.routes.backups import router as backups_router
from backend.api.routes.schedules import router as schedules_router
from backend.api.routes.tasks import router as tasks_router

# Create main router
router = APIRouter()

# Include sub-routers
router.include_router(devices_router, prefix="/devices", tags=["devices"])
router.include_router(backups_router, prefix="/devices", tags=["backups"])
router.include_router(schedules_router, prefix="/devices", tags=["schedules"])
router.include_router(tasks_router, prefix="/tasks", tags=["tasks"])
