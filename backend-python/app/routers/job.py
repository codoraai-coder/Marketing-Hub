from fastapi import APIRouter, Depends, HTTPException
from supabase import Client
from typing import List
from uuid import UUID

from ..database import get_supabase
from ..models import JOBS_TABLE
from ..schemas import JobResponse

router = APIRouter()


@router.get("/{job_id}", response_model=JobResponse)
async def get_job_status(job_id: UUID, supabase: Client = Depends(get_supabase)):
    """
    Get job status and logs
    Frontend polls this to track workflow execution
    """
    result = supabase.table(JOBS_TABLE).select("*").eq("id", str(job_id)).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Job not found")
    return result.data[0]


@router.get("/workflow/{workflow_id}", response_model=List[JobResponse])
async def get_workflow_jobs(workflow_id: UUID, supabase: Client = Depends(get_supabase)):
    """Get all jobs for a workflow"""
    result = supabase.table(JOBS_TABLE).select("*").eq("workflow_id", str(workflow_id)).execute()
    return result.data
