from fastapi import APIRouter, Depends, HTTPException, Query
from supabase import Client
from typing import List, Optional
from uuid import UUID

from ..database import get_supabase
from ..models import CONTENTS_TABLE, ContentStatus, ContentType
from ..schemas import CreateContentDto, ContentResponse, UpdateContentStatusDto

router = APIRouter()


@router.post("/", response_model=ContentResponse)
async def create_content(content: CreateContentDto, supabase: Client = Depends(get_supabase)):
    """Create new content"""
    result = supabase.table(CONTENTS_TABLE).insert(content.model_dump()).execute()
    if not result.data:
        raise HTTPException(status_code=400, detail="Failed to create content")
    return result.data[0]


@router.get("/{content_id}", response_model=ContentResponse)
async def get_content(content_id: UUID, supabase: Client = Depends(get_supabase)):
    """Get content by ID"""
    result = supabase.table(CONTENTS_TABLE).select("*").eq("id", str(content_id)).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Content not found")
    return result.data[0]


@router.get("/workspace/{workspace_id}", response_model=List[ContentResponse])
async def get_workspace_content(
    workspace_id: UUID,
    type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    supabase: Client = Depends(get_supabase)
):
    """Get all content for a workspace with optional filters"""
    query = supabase.table(CONTENTS_TABLE).select("*").eq("workspace_id", str(workspace_id))
    
    if type:
        query = query.eq("type", type)
    if status:
        query = query.eq("status", status)
    
    result = query.execute()
    return result.data


@router.post("/{content_id}/status", response_model=ContentResponse)
async def update_content_status(
    content_id: UUID,
    status_update: UpdateContentStatusDto,
    supabase: Client = Depends(get_supabase)
):
    """Update content status"""
    result = supabase.table(CONTENTS_TABLE).update({"status": status_update.status.value}).eq("id", str(content_id)).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Content not found")
    return result.data[0]
