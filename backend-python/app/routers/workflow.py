from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from supabase import Client
from typing import List, Optional
from uuid import UUID, uuid4
from datetime import datetime

from ..database import get_supabase
from ..models import WORKFLOWS_TABLE, JOBS_TABLE, JobStatus
from ..schemas import (
    CreateWorkflowDto, 
    UpdateWorkflowDto,
    WorkflowResponse, 
    WorkflowListResponse,
    WorkflowStepResponse,
    RunWorkflowResponse,
    JobResponse
)
from ..services.job_runner import JobRunner

router = APIRouter()

# Tool Registry - Available tools in the MCP system
# Must match tools registered in services/tool_registry.py
AVAILABLE_TOOLS = {
    "blog_generator",
    "image_generator",
    "caption_generator",
    "content_optimizer",
    "hashtag_generator",
    "post_to_x"  # X (Twitter) posting tool
}


def validate_workflow_steps(steps: List) -> None:
    """
    Validate workflow steps according to business rules:
    1. At least one step must exist
    2. Orders must be sequential starting from 1
    3. Tool names must exist in registry
    4. Config must be valid JSON (handled by Pydantic)
    """
    if not steps or len(steps) == 0:
        raise HTTPException(
            status_code=400, 
            detail="Workflow must have at least one step"
        )
    
    # Check sequential order
    orders = sorted([step.order for step in steps])
    expected_orders = list(range(1, len(steps) + 1))
    if orders != expected_orders:
        raise HTTPException(
            status_code=400,
            detail=f"Step orders must be sequential starting from 1. Expected {expected_orders}, got {orders}"
        )
    
    # Validate tool names
    for step in steps:
        if step.tool_name not in AVAILABLE_TOOLS:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown tool '{step.tool_name}'. Available tools: {', '.join(sorted(AVAILABLE_TOOLS))}"
            )


async def check_active_jobs(workflow_id: str, supabase: Client) -> bool:
    """Check if workflow has any active jobs (pending or running)"""
    result = supabase.table(JOBS_TABLE)\
        .select("id")\
        .eq("workflow_id", workflow_id)\
        .in_("status", [JobStatus.PENDING.value, JobStatus.RUNNING.value])\
        .execute()
    
    return len(result.data) > 0


def transform_workflow_response(workflow_data: dict, include_steps: bool = True) -> dict:
    """Transform workflow data from DB to response format with proper step structure"""
    if include_steps and workflow_data.get("steps"):
        # Convert steps array to proper format with IDs
        steps_with_ids = []
        for idx, step in enumerate(workflow_data["steps"]):
            step_response = {
                "id": f"step_{idx + 1}",
                "order": step.get("order", idx + 1),
                "name": step.get("name"),
                "tool_name": step.get("tool_name") or step.get("tool"),  # Support legacy 'tool' field
                "config": step.get("config") or step.get("input")  # Support legacy 'input' field
            }
            steps_with_ids.append(step_response)
        workflow_data["steps"] = steps_with_ids
    
    return workflow_data


@router.post("/", response_model=WorkflowResponse)
async def create_workflow(workflow: CreateWorkflowDto, supabase: Client = Depends(get_supabase)):
    """
    Create a new workflow
    
    Validates:
    - Steps must exist (at least one)
    - Orders must be sequential
    - Tool names must be registered
    """
    # Validate steps
    validate_workflow_steps(workflow.steps)
    
    # Prepare workflow data
    workflow_data = {
        "workspace_id": str(workflow.workspace_id),
        "name": workflow.name,
        "description": workflow.description,
        "target_platform": workflow.target_platform.value if workflow.target_platform else None,
        "steps": [step.model_dump() for step in workflow.steps],
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }
    
    result = supabase.table(WORKFLOWS_TABLE).insert(workflow_data).execute()
    if not result.data:
        raise HTTPException(status_code=400, detail="Failed to create workflow")
    
    # Transform response
    response_data = transform_workflow_response(result.data[0])
    return response_data


@router.get("/", response_model=List[WorkflowListResponse])
async def list_workflows(
    workspace_id: Optional[UUID] = None,
    limit: int = 50,
    offset: int = 0,
    supabase: Client = Depends(get_supabase)
):
    """
    List all workflows for a workspace
    Returns summary view without step details
    Includes last run information
    
    Query Parameters:
    - workspace_id: Required - UUID of the workspace to filter by
    - limit: Optional - Max number of results (default: 50)
    - offset: Optional - Pagination offset (default: 0)
    """
    # Validate workspace_id is provided
    if workspace_id is None:
        raise HTTPException(
            status_code=400,
            detail="workspace_id query parameter is required. Example: GET /api/workflows/?workspace_id=<your-uuid>"
        )
    
    # Get workflows with pagination
    workflows_result = supabase.table(WORKFLOWS_TABLE)\
        .select("*")\
        .eq("workspace_id", str(workspace_id))\
        .is_("deleted_at", "null")\
        .order("created_at", desc=True)\
        .range(offset, offset + limit - 1)\
        .execute()
    
    workflows = []
    for workflow in workflows_result.data:
        # Get last job for this workflow
        last_job_result = supabase.table(JOBS_TABLE)\
            .select("started_at, status")\
            .eq("workflow_id", workflow["id"])\
            .order("started_at", desc=True)\
            .limit(1)\
            .execute()
        
        # Add last run info
        workflow_summary = {
            "id": workflow["id"],
            "name": workflow["name"],
            "description": workflow.get("description"),
            "target_platform": workflow.get("target_platform"),
            "created_at": workflow["created_at"],
            "last_run_at": last_job_result.data[0]["started_at"] if last_job_result.data else None,
            "last_run_status": last_job_result.data[0]["status"] if last_job_result.data else None
        }
        workflows.append(workflow_summary)
    
    return workflows


@router.get("/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(workflow_id: UUID, supabase: Client = Depends(get_supabase)):
    """
    Get workflow by ID with full details including steps
    """
    result = supabase.table(WORKFLOWS_TABLE)\
        .select("*")\
        .eq("id", str(workflow_id))\
        .is_("deleted_at", "null")\
        .execute()
    
    if not result.data:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    # Transform response with proper step structure
    response_data = transform_workflow_response(result.data[0])
    return response_data


@router.get("/workspace/{workspace_id}", response_model=List[WorkflowResponse])
async def get_workspace_workflows(workspace_id: UUID, supabase: Client = Depends(get_supabase)):
    """
    DEPRECATED: Use GET / with workspace_id query parameter instead
    Get all workflows for a workspace (kept for backward compatibility)
    """
    result = supabase.table(WORKFLOWS_TABLE)\
        .select("*")\
        .eq("workspace_id", str(workspace_id))\
        .is_("deleted_at", "null")\
        .execute()
    
    # Transform all workflows
    workflows = [transform_workflow_response(w) for w in result.data]
    return workflows


@router.put("/{workflow_id}", response_model=WorkflowResponse)
async def update_workflow(
    workflow_id: UUID,
    workflow_update: UpdateWorkflowDto,
    supabase: Client = Depends(get_supabase)
):
    """
    Update an existing workflow
    
    Rules:
    - Cannot update while jobs are running
    - Steps are fully replaced (not merged)
    - Validates new steps if provided
    """
    # Check if workflow exists
    existing = supabase.table(WORKFLOWS_TABLE)\
        .select("*")\
        .eq("id", str(workflow_id))\
        .is_("deleted_at", "null")\
        .execute()
    
    if not existing.data:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    # Check for active jobs
    if await check_active_jobs(str(workflow_id), supabase):
        raise HTTPException(
            status_code=409,
            detail="Cannot update workflow while jobs are running. Please wait for active jobs to complete."
        )
    
    # Build update data (only include provided fields)
    update_data = {"updated_at": datetime.utcnow().isoformat()}
    
    if workflow_update.name is not None:
        update_data["name"] = workflow_update.name
    
    if workflow_update.description is not None:
        update_data["description"] = workflow_update.description
    
    if workflow_update.target_platform is not None:
        update_data["target_platform"] = workflow_update.target_platform.value
    
    if workflow_update.steps is not None:
        # Validate new steps
        validate_workflow_steps(workflow_update.steps)
        update_data["steps"] = [step.model_dump() for step in workflow_update.steps]
    
    # Perform update
    result = supabase.table(WORKFLOWS_TABLE)\
        .update(update_data)\
        .eq("id", str(workflow_id))\
        .execute()
    
    if not result.data:
        raise HTTPException(status_code=400, detail="Failed to update workflow")
    
    # Transform response
    response_data = transform_workflow_response(result.data[0])
    return response_data


@router.delete("/{workflow_id}", status_code=204)
async def delete_workflow(
    workflow_id: UUID,
    supabase: Client = Depends(get_supabase)
):
    """
    Delete a workflow (soft delete)
    
    Rules:
    - Cannot delete if active jobs exist
    - Sets deleted_at timestamp instead of hard delete
    """
    # Check if workflow exists
    existing = supabase.table(WORKFLOWS_TABLE)\
        .select("id")\
        .eq("id", str(workflow_id))\
        .is_("deleted_at", "null")\
        .execute()
    
    if not existing.data:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    # Check for active jobs
    if await check_active_jobs(str(workflow_id), supabase):
        raise HTTPException(
            status_code=409,
            detail="Cannot delete workflow while jobs are running. Please wait for active jobs to complete."
        )
    
    # Soft delete
    result = supabase.table(WORKFLOWS_TABLE)\
        .update({"deleted_at": datetime.utcnow().isoformat()})\
        .eq("id", str(workflow_id))\
        .execute()
    
    if not result.data:
        raise HTTPException(status_code=400, detail="Failed to delete workflow")
    
    return None


@router.post("/{workflow_id}/run", response_model=RunWorkflowResponse)
async def run_workflow(
    workflow_id: UUID,
    background_tasks: BackgroundTasks,
    supabase: Client = Depends(get_supabase)
):
    """
    Trigger workflow execution (MOST IMPORTANT ENDPOINT)
    
    This endpoint:
    1. Validates workflow exists
    2. Creates a Job record with status=pending
    3. Spawns background execution task
    4. Returns immediately with job_id
    
    The actual execution happens asynchronously via JobRunner.
    Frontend polls GET /api/jobs/{job_id} to track progress.
    """
    # Validate workflow exists and is not deleted
    workflow_result = supabase.table(WORKFLOWS_TABLE)\
        .select("*")\
        .eq("id", str(workflow_id))\
        .is_("deleted_at", "null")\
        .execute()
    
    if not workflow_result.data:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    workflow = workflow_result.data[0]
    
    # Validate workflow has steps
    if not workflow.get("steps") or len(workflow["steps"]) == 0:
        raise HTTPException(
            status_code=400, 
            detail="Cannot run workflow with no steps"
        )
    
    # Create job record
    started_at = datetime.utcnow()
    job_data = {
        "workflow_id": str(workflow_id),
        "status": JobStatus.PENDING.value,
        "started_at": started_at.isoformat(),
        "progress": 0,
        "current_step": 0,
        "logs": {
            "message": "Job created and queued for execution",
            "workflow_name": workflow["name"],
            "step_count": len(workflow["steps"])
        }
    }
    
    job_result = supabase.table(JOBS_TABLE).insert(job_data).execute()
    
    if not job_result.data:
        raise HTTPException(status_code=400, detail="Failed to create job")
    
    job = job_result.data[0]
    job_id = job["id"]
    
    # Spawn background execution task
    job_runner = JobRunner(supabase)
    background_tasks.add_task(job_runner.execute_job, job_id)
    
    # Return immediately
    return {
        "job_id": job_id,
        "workflow_id": workflow_id,
        "status": JobStatus.PENDING,
        "started_at": started_at
    }
