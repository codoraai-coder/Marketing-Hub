"""
Posting Router - Handles posting jobs and user-assisted content publishing
"""
from fastapi import APIRouter, HTTPException, status
from typing import List
from uuid import UUID
from datetime import datetime

from app.database import supabase
from app.models import POSTING_JOBS_TABLE, CONTENT_TABLE
from app.schemas import (
    PostingJobResponse,
    UpdatePostingJobDto,
    PostingStatus,
    ContentStatus
)
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/posting-jobs", tags=["posting"])


@router.get("/{job_id}", response_model=PostingJobResponse)
async def get_posting_job(job_id: UUID):
    """
    Get a specific posting job by ID
    
    Returns the posting job with prepared payload that user can use to manually post.
    """
    try:
        response = supabase.table(POSTING_JOBS_TABLE)\
            .select("*")\
            .eq("id", str(job_id))\
            .execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Posting job {job_id} not found"
            )
        
        return response.data[0]
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching posting job {job_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch posting job: {str(e)}"
        )


@router.get("/workspace/{workspace_id}/ready", response_model=List[PostingJobResponse])
async def list_ready_posting_jobs(
    workspace_id: UUID,
    limit: int = 50
):
    """
    List all posting jobs with status='ready' for a workspace
    
    These are jobs that have been prepared by MCP and are waiting for user to post.
    """
    try:
        response = supabase.table(POSTING_JOBS_TABLE)\
            .select("*")\
            .eq("workspace_id", str(workspace_id))\
            .eq("status", PostingStatus.READY.value)\
            .order("created_at", desc=True)\
            .limit(limit)\
            .execute()
        
        return response.data or []
    
    except Exception as e:
        logger.error(f"Error listing ready posting jobs for workspace {workspace_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list posting jobs: {str(e)}"
        )


@router.get("/workspace/{workspace_id}/all", response_model=List[PostingJobResponse])
async def list_all_posting_jobs(
    workspace_id: UUID,
    status_filter: str = None,
    limit: int = 100
):
    """
    List all posting jobs for a workspace with optional status filter
    """
    try:
        query = supabase.table(POSTING_JOBS_TABLE)\
            .select("*")\
            .eq("workspace_id", str(workspace_id))
        
        if status_filter:
            query = query.eq("status", status_filter)
        
        response = query.order("created_at", desc=True)\
            .limit(limit)\
            .execute()
        
        return response.data or []
    
    except Exception as e:
        logger.error(f"Error listing posting jobs for workspace {workspace_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list posting jobs: {str(e)}"
        )


@router.post("/{job_id}/mark-posted", response_model=PostingJobResponse)
async def mark_posting_job_as_posted(job_id: UUID):
    """
    Mark a posting job as posted after user manually posts to LinkedIn
    
    This also updates the associated content status to 'posted' and sets posted_at timestamp.
    """
    try:
        # Step 1: Get the posting job
        job_response = supabase.table(POSTING_JOBS_TABLE)\
            .select("*")\
            .eq("id", str(job_id))\
            .execute()
        
        if not job_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Posting job {job_id} not found"
            )
        
        posting_job = job_response.data[0]
        content_id = posting_job['content_id']
        
        # Step 2: Update posting job status to 'posted'
        now = datetime.utcnow().isoformat()
        
        job_update_response = supabase.table(POSTING_JOBS_TABLE)\
            .update({
                "status": PostingStatus.POSTED.value,
                "posted_at": now
            })\
            .eq("id", str(job_id))\
            .execute()
        
        if not job_update_response.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update posting job status"
            )
        
        # Step 3: Update content status to 'posted'
        content_update_response = supabase.table(CONTENT_TABLE)\
            .update({
                "status": ContentStatus.POSTED.value,
                "posted_at": now
            })\
            .eq("id", content_id)\
            .execute()
        
        if not content_update_response.data:
            logger.warning(f"Failed to update content {content_id} status to posted")
        
        logger.info(f"Posting job {job_id} marked as posted. Content {content_id} updated.")
        
        return job_update_response.data[0]
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error marking posting job {job_id} as posted: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to mark posting job as posted: {str(e)}"
        )


@router.post("/{job_id}/mark-failed", response_model=PostingJobResponse)
async def mark_posting_job_as_failed(
    job_id: UUID,
    error_message: str = "User reported posting failed"
):
    """
    Mark a posting job as failed if user encounters errors while posting
    
    This allows tracking of failed attempts and can be used for retry logic.
    """
    try:
        # Get current job to increment retry count
        job_response = supabase.table(POSTING_JOBS_TABLE)\
            .select("*")\
            .eq("id", str(job_id))\
            .execute()
        
        if not job_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Posting job {job_id} not found"
            )
        
        current_job = job_response.data[0]
        new_retry_count = current_job.get('retry_count', 0) + 1
        
        # Update posting job status to 'failed'
        update_response = supabase.table(POSTING_JOBS_TABLE)\
            .update({
                "status": PostingStatus.FAILED.value,
                "error_message": error_message,
                "retry_count": new_retry_count
            })\
            .eq("id", str(job_id))\
            .execute()
        
        if not update_response.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update posting job status"
            )
        
        logger.info(f"Posting job {job_id} marked as failed. Retry count: {new_retry_count}")
        
        return update_response.data[0]
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error marking posting job {job_id} as failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to mark posting job as failed: {str(e)}"
        )


@router.post("/{job_id}/retry", response_model=PostingJobResponse)
async def retry_posting_job(job_id: UUID):
    """
    Reset a failed posting job back to 'ready' status for retry
    
    This allows users to retry posting after fixing issues.
    """
    try:
        # Get the posting job
        job_response = supabase.table(POSTING_JOBS_TABLE)\
            .select("*")\
            .eq("id", str(job_id))\
            .execute()
        
        if not job_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Posting job {job_id} not found"
            )
        
        posting_job = job_response.data[0]
        
        if posting_job['status'] == PostingStatus.POSTED.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot retry a posting job that has already been posted"
            )
        
        # Reset to ready status
        update_response = supabase.table(POSTING_JOBS_TABLE)\
            .update({
                "status": PostingStatus.READY.value,
                "error_message": None
            })\
            .eq("id", str(job_id))\
            .execute()
        
        if not update_response.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retry posting job"
            )
        
        logger.info(f"Posting job {job_id} reset to ready for retry")
        
        return update_response.data[0]
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrying posting job {job_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retry posting job: {str(e)}"
        )
