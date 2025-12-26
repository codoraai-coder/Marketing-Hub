"""
Test the Job Execution Engine
Creates a workflow and runs it to verify execution
"""
import requests
import json
import time
from uuid import uuid4

BASE_URL = "http://localhost:8000/api"

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def test_job_execution():
    """Test complete job execution flow"""
    
    # 1. Create workspace
    print_section("1. CREATE WORKSPACE")
    workspace_data = {
        "owner_user_id": str(uuid4()),
        "name": "Test Execution Workspace"
    }
    response = requests.post(f"{BASE_URL}/workspaces", json=workspace_data)
    workspace = response.json()
    workspace_id = workspace["id"]
    print(f"✅ Workspace created: {workspace_id}")
    
    # 2. Create workflow with blog and image generation
    print_section("2. CREATE WORKFLOW")
    workflow_data = {
        "workspace_id": workspace_id,
        "name": "Blog + Image Pipeline",
        "description": "Generate blog post and motivational image",
        "target_platform": "linkedin",
        "steps": [
            {
                "order": 1,
                "name": "Generate Blog Post",
                "tool_name": "blog_generator",
                "config": {
                    "topic": "The Future of AI in Business",
                    "tone": "professional",
                    "length": "medium"
                }
            },
            {
                "order": 2,
                "name": "Generate Motivational Image",
                "tool_name": "image_generator",
                "config": {
                    "theme": "success",
                    "style": "professional"
                }
            }
        ]
    }
    
    response = requests.post(f"{BASE_URL}/workflows", json=workflow_data)
    workflow = response.json()
    workflow_id = workflow["id"]
    print(f"✅ Workflow created: {workflow_id}")
    print(f"   Steps: {len(workflow['steps'])}")
    
    # 3. Run workflow
    print_section("3. RUN WORKFLOW")
    response = requests.post(f"{BASE_URL}/workflows/{workflow_id}/run")
    run_result = response.json()
    job_id = run_result["job_id"]
    print(f"✅ Workflow execution triggered")
    print(f"   Job ID: {job_id}")
    print(f"   Status: {run_result['status']}")
    
    # 4. Poll job status
    print_section("4. MONITOR JOB EXECUTION")
    max_polls = 60  # 2 minutes max
    poll_interval = 2  # seconds
    
    for i in range(max_polls):
        time.sleep(poll_interval)
        
        response = requests.get(f"{BASE_URL}/jobs/{job_id}")
        job = response.json()
        
        status = job["status"]
        progress = job.get("progress", 0)
        current_step = job.get("current_step", 0)
        logs = job.get("logs", {})
        message = logs.get("message", "")
        
        print(f"[Poll {i+1}] Status: {status} | Progress: {progress}% | Step: {current_step} | {message}")
        
        if status == "completed":
            print_section("✅ JOB COMPLETED SUCCESSFULLY!")
            print("Final Results:")
            print(json.dumps(logs, indent=2))
            return True
        
        elif status == "failed":
            print_section("❌ JOB FAILED")
            print("Error Details:")
            print(json.dumps(logs, indent=2))
            return False
        
        elif status == "running":
            step_detail = logs.get("progress_detail", "")
            if step_detail:
                print(f"   └─ {step_detail}")
    
    print_section("⚠️ TIMEOUT")
    print("Job did not complete within timeout period")
    return False

if __name__ == "__main__":
    print("\n" + "="*60)
    print("  🧪 TESTING JOB EXECUTION ENGINE")
    print("="*60)
    print("\nMake sure the server is running:")
    print("  cd backend-python && python -m uvicorn main:app --reload")
    print()
    
    try:
        success = test_job_execution()
        
        if success:
            print("\n" + "="*60)
            print("  🎉 ALL TESTS PASSED - MCP IS ALIVE!")
            print("="*60)
        else:
            print("\n" + "="*60)
            print("  ⚠️ TEST FAILED - Check logs above")
            print("="*60)
            
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Cannot connect to server")
        print("Start with: cd backend-python && python -m uvicorn main:app --reload")
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
