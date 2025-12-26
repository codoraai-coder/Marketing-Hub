"""
Content Router - CRUD APIs for managing tool outputs
Makes content first-class citizens with approval workflows
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime
from uuid import UUID

from ..database import supabase
from ..models import CONTENT_TABLE, ContentStatus, ContentType
from ..schemas import ContentResponse, UpdateContentDto

router = APIRouter()


@router.get("/", response_model=List[ContentResponse])
async def list_content(
    workspace_id: Optional[str] = Query(None),
    job_id: Optional[str] = Query(None),
    content_type: Optional[ContentType] = Query(None),
    status: Optional[ContentStatus] = Query(None),
    limit: int = Query(50, le=100)
):
    """
    List all content with optional filters
    
    Query Parameters:
    - workspace_id: Filter by workspace
    - job_id: Filter by job
    - content_type: Filter by content type (blog_post, image, caption, etc.)
    - status: Filter by status (draft, approved, used, posted)
    - limit: Maximum results (default 50, max 100)
    """
    query = supabase.table(CONTENT_TABLE).select("*")
    
    # Apply filters
    if workspace_id:
        query = query.eq("workspace_id", workspace_id)
    if job_id:
        query = query.eq("job_id", job_id)
    if content_type:
        query = query.eq("content_type", content_type.value)
    if status:
        query = query.eq("status", status.value)
    
    # Only non-deleted content
    query = query.is_("deleted_at", "null")
    
    # Order by created_at desc
    query = query.order("created_at", desc=True).limit(limit)
    
    result = query.execute()
    
    return result.data


@router.get("/{content_id}", response_model=ContentResponse)
async def get_content(content_id: str):
    """Get a specific content by ID"""
    result = supabase.table(CONTENT_TABLE)\
        .select("*")\
        .eq("id", content_id)\
        .is_("deleted_at", "null")\
        .execute()
    
    if not result.data:
        raise HTTPException(status_code=404, detail="Content not found")
    
    return result.data[0]


@router.patch("/{content_id}", response_model=ContentResponse)
async def update_content(content_id: str, update_data: UpdateContentDto):
    """
    Update content metadata or status
    
    Use this to:
    - Approve content: Set status to 'approved'
    - Mark as used: Set status to 'used'
    - Mark as posted: Set status to 'posted'
    - Update title or data
    """
    # Check content exists
    existing = supabase.table(CONTENT_TABLE)\
        .select("*")\
        .eq("id", content_id)\
        .is_("deleted_at", "null")\
        .execute()
    
    if not existing.data:
        raise HTTPException(status_code=404, detail="Content not found")
    
    # Build update payload
    update_payload = {
        "updated_at": datetime.utcnow().isoformat()
    }
    
    if update_data.title is not None:
        update_payload["title"] = update_data.title
    
    if update_data.data is not None:
        update_payload["data"] = update_data.data
    
    if update_data.status is not None:
        update_payload["status"] = update_data.status.value
        
        # Set lifecycle timestamps
        if update_data.status == ContentStatus.APPROVED:
            update_payload["approved_at"] = datetime.utcnow().isoformat()
        elif update_data.status == ContentStatus.POSTED:
            update_payload["posted_at"] = datetime.utcnow().isoformat()
    
    # Update in database
    result = supabase.table(CONTENT_TABLE)\
        .update(update_payload)\
        .eq("id", content_id)\
        .execute()
    
    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to update content")
    
    return result.data[0]


@router.delete("/{content_id}")
async def delete_content(content_id: str):
    """
    Soft delete content
    
    Content is not actually removed, just marked as deleted
    This preserves audit trails and analytics attachments
    """
    # Check content exists
    existing = supabase.table(CONTENT_TABLE)\
        .select("*")\
        .eq("id", content_id)\
        .is_("deleted_at", "null")\
        .execute()
    
    if not existing.data:
        raise HTTPException(status_code=404, detail="Content not found")
    
    # Soft delete
    result = supabase.table(CONTENT_TABLE)\
        .update({"deleted_at": datetime.utcnow().isoformat()})\
        .eq("id", content_id)\
        .execute()
    
    return {
        "message": "Content deleted successfully",
        "content_id": content_id,
        "deleted_at": datetime.utcnow().isoformat()
    }


@router.post("/{content_id}/approve", response_model=ContentResponse)
async def approve_content(content_id: str):
    """
    Approve content for use
    
    Shortcut endpoint to set status to 'approved'
    """
    return await update_content(
        content_id, 
        UpdateContentDto(status=ContentStatus.APPROVED)
    )


@router.get("/workspace/{workspace_id}/pending", response_model=List[ContentResponse])
async def get_pending_content(workspace_id: str, limit: int = Query(20, le=100)):
    """
    Get all pending (draft) content for a workspace
    
    Useful for approval workflows
    """
    result = supabase.table(CONTENT_TABLE)\
        .select("*")\
        .eq("workspace_id", workspace_id)\
        .eq("status", ContentStatus.DRAFT.value)\
        .is_("deleted_at", "null")\
        .order("created_at", desc=True)\
        .limit(limit)\
        .execute()
    
    return result.data
