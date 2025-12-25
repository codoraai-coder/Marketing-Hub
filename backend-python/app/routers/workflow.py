from fastapi import APIRouter, Depends, HTTPException
from supabase import Client
from typing import List
from uuid import UUID
from datetime import datetime

from ..database import get_supabase
from ..models import WORKFLOWS_TABLE, JOBS_TABLE, JobStatus
from ..schemas import CreateWorkflowDto, WorkflowResponse, JobResponse

router = APIRouter()


@router.post("/", response_model=WorkflowResponse)
async def create_workflow(workflow: CreateWorkflowDto, supabase: Client = Depends(get_supabase)):
    """Create a new workflow"""
    workflow_data = workflow.model_dump()
    workflow_data['steps'] = [step.model_dump() for step in workflow.steps]
    
    result = supabase.table(WORKFLOWS_TABLE).insert(workflow_data).execute()
    if not result.data:
        raise HTTPException(status_code=400, detail="Failed to create workflow")
    return result.data[0]


@router.get("/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(workflow_id: UUID, supabase: Client = Depends(get_supabase)):
    """Get workflow by ID"""
    result = supabase.table(WORKFLOWS_TABLE).select("*").eq("id", str(workflow_id)).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return result.data[0]


@router.get("/workspace/{workspace_id}", response_model=List[WorkflowResponse])
async def get_workspace_workflows(workspace_id: UUID, supabase: Client = Depends(get_supabase)):
    """Get all workflows for a workspace"""
    result = supabase.table(WORKFLOWS_TABLE).select("*").eq("workspace_id", str(workspace_id)).execute()
    return result.data


@router.post("/{workflow_id}/run", response_model=dict)
async def run_workflow(workflow_id: UUID, supabase: Client = Depends(get_supabase)):
    """
    MCP EXECUTION ENDPOINT - This is the heart of the system
    Frontend expresses intent: "run this workflow"
    MCP decides execution
    """
    workflow_result = supabase.table(WORKFLOWS_TABLE).select("*").eq("id", str(workflow_id)).execute()
    if not workflow_result.data:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    # Create a new job
    job_data = {
        "workflow_id": str(workflow_id),
        "status": JobStatus.PENDING.value,
        "started_at": datetime.utcnow().isoformat()
    }
    job_result = supabase.table(JOBS_TABLE).insert(job_data).execute()
    
    if not job_result.data:
        raise HTTPException(status_code=400, detail="Failed to create job")
    
    # TODO: Implement execution engine
    # For now, just return the job
    return {
        "message": "Workflow execution started",
        "job_id": job_result.data[0]["id"],
        "status": job_result.data[0]["status"]
    }
