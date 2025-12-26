from fastapi import APIRouter, Depends, HTTPException
from supabase import Client
from typing import List
from uuid import UUID

from ..database import get_supabase
from ..models import WORKSPACES_TABLE
from ..schemas import CreateWorkspaceDto, WorkspaceResponse

router = APIRouter()


@router.post("/", response_model=WorkspaceResponse)
async def create_workspace(workspace: CreateWorkspaceDto, supabase: Client = Depends(get_supabase)):
    """Create a new workspace"""
    workspace_data = {
        "owner_user_id": str(workspace.owner_user_id),
        "name": workspace.name
    }
    result = supabase.table(WORKSPACES_TABLE).insert(workspace_data).execute()
    if not result.data:
        raise HTTPException(status_code=400, detail="Failed to create workspace")
    return result.data[0]


@router.get("/{workspace_id}", response_model=WorkspaceResponse)
async def get_workspace(workspace_id: UUID, supabase: Client = Depends(get_supabase)):
    """Get workspace by ID"""
    result = supabase.table(WORKSPACES_TABLE).select("*").eq("id", str(workspace_id)).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return result.data[0]


@router.get("/user/{user_id}", response_model=List[WorkspaceResponse])
async def get_user_workspaces(user_id: UUID, supabase: Client = Depends(get_supabase)):
    """Get all workspaces for a user"""
    result = supabase.table(WORKSPACES_TABLE).select("*").eq("owner_user_id", str(user_id)).execute()
    return result.data
