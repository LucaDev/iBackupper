"""
API routes for task operations.
"""
from fastapi import APIRouter, HTTPException, status

from backend.core.backup_manager import BackupManager

router = APIRouter()


@router.get("/")
async def list_tasks():
    """
    List all background tasks.
    
    Returns:
        List of all background tasks
    """
    tasks = BackupManager.get_all_tasks()
    return list(tasks.values())


@router.get("/{task_id}")
async def get_task(task_id: str):
    """
    Get information for a specific task.
    
    Args:
        task_id: The task ID
        
    Returns:
        Task information
    """
    task_info = BackupManager.get_task_status(task_id)
    
    if not task_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found"
        )
    
    return task_info


@router.delete("/{task_id}")
async def cancel_task(task_id: str):
    """
    Cancel a running task.
    
    Args:
        task_id: The task ID
        
    Returns:
        Success message
    """
    success = BackupManager.cancel_task(task_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel task with ID {task_id}"
        )
    
    return {"message": f"Task with ID {task_id} cancelled successfully"}
