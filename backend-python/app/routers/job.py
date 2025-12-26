from fastapi import APIRouter, Depends, HTTPException, Query
from supabase import Client
from typing import List, Optional
from uuid import UUID

from ..database import get_supabase
from ..models import JOBS_TABLE
from ..schemas import JobResponse

router = APIRouter()


@router.get("/{job_id}", response_model=JobResponse)
async def get_job_status(job_id: UUID, supabase: Client = Depends(get_supabase)):
    """
    Get job status and logs
    
    Frontend polls this endpoint to track workflow execution progress.
    Returns full job details including:
    - Current status (pending, running, completed, failed)
    - Execution logs
    - Timestamps
    """
    result = supabase.table(JOBS_TABLE).select("*").eq("id", str(job_id)).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Job not found")
    return result.data[0]


@router.get("/workflow/{workflow_id}", response_model=List[JobResponse])
async def get_workflow_jobs(
    workflow_id: UUID,
    status: Optional[str] = Query(None, description="Filter by job status"),
    limit: Optional[int] = Query(10, description="Number of jobs to return"),
    supabase: Client = Depends(get_supabase)
):
    """
    Get all jobs for a specific workflow
    
    Useful for:
    - Viewing execution history
    - Debugging failed runs
    - Analyzing workflow performance
    
    Supports filtering by status and limiting results.
    """
    query = supabase.table(JOBS_TABLE)\
        .select("*")\
        .eq("workflow_id", str(workflow_id))\
        .order("started_at", desc=True)\
        .limit(limit)
    
    if status:
        query = query.eq("status", status)
    
    result = query.execute()
    return result.data
