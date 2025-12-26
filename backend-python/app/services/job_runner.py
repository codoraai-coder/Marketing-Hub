"""
Job Runner - Executes workflow jobs step by step
This is the CORE MCP execution logic
"""
from supabase import Client
from typing import Dict, Any
import logging
from datetime import datetime
from uuid import UUID

from ..models import WORKFLOWS_TABLE, JOBS_TABLE, CONTENT_TABLE, JobStatus, ContentType, ContentStatus
from .tool_registry import tool_registry

logger = logging.getLogger(__name__)

class JobRunner:
    """Executes workflow jobs by running steps sequentially"""
    
    def __init__(self, supabase: Client):
        self.supabase = supabase
    
    async def execute_job(self, job_id: str):
        """
        Execute a job by running all workflow steps
        
        This is the Master Control Program runtime execution logic:
        1. Load job and workflow
        2. Mark job as running
        3. Execute each step sequentially
        4. Update progress and logs in real-time
        5. Mark job as completed or failed
        """
        try:
            # Load job
            job = await self._get_job(job_id)
            if not job:
                logger.error(f"Job {job_id} not found")
                return
            
            # Load workflow
            workflow = await self._get_workflow(job["workflow_id"])
            if not workflow:
                logger.error(f"Workflow {job['workflow_id']} not found")
                await self._update_job_status(job_id, JobStatus.FAILED, 
                                             {"error": "Workflow not found"})
                return
            
            # Mark job as running
            logger.info(f"Job {job_id}: Starting execution for workflow '{workflow['name']}'")
            await self._update_job_status(job_id, JobStatus.RUNNING, {
                "message": "Job execution started",
                "workflow_name": workflow["name"]
            })
            
            # Execute steps
            steps = workflow.get("steps", [])
            total_steps = len(steps)
            
            if total_steps == 0:
                await self._update_job_status(job_id, JobStatus.FAILED, 
                                             {"error": "No steps to execute"})
                return
            
            step_results = []
            last_content_id = None  # Track content_id from previous step
            
            for step_index, step in enumerate(steps):
                current_step = step_index + 1
                step_name = step.get("name", f"Step {current_step}")
                tool_name = step.get("tool_name")
                config = step.get("config", {}).copy()  # Copy to avoid mutating original
                
                # Inject context from previous steps if needed
                # This allows steps like "Post to X" to get content_id from previous step
                if last_content_id and "content_id" not in config:
                    config["content_id"] = str(last_content_id)
                if "workspace_id" not in config:
                    config["workspace_id"] = workflow["workspace_id"]
                
                # Update current step - Starting
                logger.info(f"Job {job_id}: Starting step {current_step}/{total_steps}: {step_name}")
                await self._update_job_progress(
                    job_id, 
                    current_step, 
                    int((step_index / total_steps) * 100),
                    {
                        "message": f"Starting {step_name}",
                        "step": step_name,
                        "tool": tool_name,
                        "progress_detail": f"Step {current_step} of {total_steps}"
                    }
                )
                
                try:
                    # Execute tool
                    logger.info(f"Job {job_id}: Executing tool '{tool_name}' with config: {config}")
                    result = await tool_registry.execute_tool(tool_name, config)
                    step_results.append(result)
                    
                    # Save content to database
                    # Generate step_id from order (steps don't have id in DB, only in API responses)
                    workflow_step_id = f"step_{step.get('order', step_index + 1)}"
                    content_id = await self._save_content(
                        workspace_id=workflow["workspace_id"],
                        job_id=job_id,
                        workflow_step_id=workflow_step_id,
                        tool_name=tool_name,
                        result=result
                    )
                    
                    # Track content_id for next step
                    last_content_id = content_id
                    
                    # Log success
                    logger.info(f"Job {job_id}: Completed step {current_step}/{total_steps}: {step_name}, content_id: {content_id}")
                    await self._update_job_progress(
                        job_id,
                        current_step,
                        int(((step_index + 1) / total_steps) * 100),
                        {
                            "message": f"Completed {step_name}",
                            "step": step_name,
                            "result": result,
                            "content_id": str(content_id),
                            "progress_detail": f"Step {current_step} of {total_steps} complete"
                        }
                    )
                    
                except Exception as e:
                    logger.error(f"Job {job_id}: Step {step_name} failed: {str(e)}", exc_info=True)
                    await self._update_job_status(job_id, JobStatus.FAILED, {
                        "error": f"Step '{step_name}' failed: {str(e)}",
                        "failed_step": step_name,
                        "step_index": current_step,
                        "total_steps": total_steps
                    })
                    return
            
            # Mark job as completed
            logger.info(f"Job {job_id}: All {total_steps} steps completed successfully")
            await self._update_job_status(job_id, JobStatus.COMPLETED, {
                "message": "All steps completed successfully",
                "total_steps": total_steps,
                "results": step_results
            })
            
        except Exception as e:
            logger.error(f"Job {job_id} execution failed with unexpected error: {str(e)}", exc_info=True)
            await self._update_job_status(job_id, JobStatus.FAILED, {
                "error": f"Job execution error: {str(e)}"
            })
    
    async def _get_job(self, job_id: str) -> Dict[str, Any]:
        """Fetch job from database"""
        result = self.supabase.table(JOBS_TABLE).select("*").eq("id", job_id).execute()
        return result.data[0] if result.data else None
    
    async def _get_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Fetch workflow from database"""
        result = self.supabase.table(WORKFLOWS_TABLE).select("*").eq("id", workflow_id).execute()
        return result.data[0] if result.data else None
    
    async def _update_job_status(self, job_id: str, status: JobStatus, logs: Dict[str, Any]):
        """Update job status and logs"""
        update_data = {
            "status": status.value,
            "logs": logs
        }
        
        if status == JobStatus.COMPLETED:
            update_data["completed_at"] = datetime.utcnow().isoformat()
            update_data["progress"] = 100
        
        self.supabase.table(JOBS_TABLE).update(update_data).eq("id", job_id).execute()
    
    async def _update_job_progress(self, job_id: str, current_step: int, 
                                   progress: int, logs: Dict[str, Any]):
        """Update job progress and current step"""
        update_data = {
            "current_step": current_step,
            "progress": progress,
            "logs": logs
        }
        
        self.supabase.table(JOBS_TABLE).update(update_data).eq("id", job_id).execute()
    
    async def _save_content(self, workspace_id: str, job_id: str, 
                           workflow_step_id: str, tool_name: str, 
                           result: Dict[str, Any], auto_approve: bool = True) -> str:
        """
        Save tool output as content in the database
        
        This makes tool outputs first-class citizens that can be:
        - Approved before use
        - Reused across workflows
        - Attached to analytics
        - Posted to social media
        
        Args:
            auto_approve: If True, content is auto-approved for workflow automation.
                         Set to False if manual review is required.
        """
        # Map tool names to content types
        tool_to_content_type = {
            "blog_generator": ContentType.BLOG_POST,
            "image_generator": ContentType.IMAGE,
            "caption_generator": ContentType.CAPTION,
            "hashtag_generator": ContentType.HASHTAGS,
            "content_optimizer": ContentType.OPTIMIZED_CONTENT
        }
        
        content_type = tool_to_content_type.get(tool_name)
        if not content_type:
            logger.warning(f"Unknown tool '{tool_name}', defaulting to OPTIMIZED_CONTENT")
            content_type = ContentType.OPTIMIZED_CONTENT
        
        # Extract the actual content data from the tool result
        # Tool results have structure: {"status": "success", "tool": "...", "result": {...}}
        # We want to save just the inner "result" data
        actual_data = result.get("result", result) if isinstance(result, dict) else result
        
        # Extract title from result if available
        title = None
        if "topic" in actual_data:
            title = actual_data["topic"]
        elif "caption" in actual_data:
            title = actual_data["caption"][:100]  # First 100 chars as title
        elif "topic" in result:
            title = result["topic"]
        
        # Auto-approve for workflow automation, or draft for manual review
        status = ContentStatus.APPROVED.value if auto_approve else ContentStatus.DRAFT.value
        
        # Create content record
        content_data = {
            "workspace_id": str(workspace_id),
            "job_id": str(job_id),
            "workflow_step_id": str(workflow_step_id),
            "content_type": content_type.value,
            "title": title,
            "data": actual_data,  # Save the inner result data, not the wrapper
            "status": status,
            "created_at": datetime.utcnow().isoformat()
        }
        
        insert_result = self.supabase.table(CONTENT_TABLE).insert(content_data).execute()
        
        if insert_result.data:
            content_id = insert_result.data[0]["id"]
            logger.info(f"Saved content {content_id} for job {job_id}")
            return content_id
        else:
            logger.error(f"Failed to save content for job {job_id}")
            return None

