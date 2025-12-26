"""
Quick Test Script for Workflow APIs
Run this after starting the server to verify implementation
"""

import requests
import json
from uuid import uuid4

BASE_URL = "http://localhost:8000/api"

def print_response(name, response):
    print(f"\n{'='*60}")
    print(f"TEST: {name}")
    print(f"Status: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")
    print(f"{'='*60}")

def test_workflow_apis():
    """Test all workflow endpoints"""
    
    # 1. Create a test workspace first
    owner_user_id = str(uuid4())
    create_workspace_data = {
        "owner_user_id": owner_user_id,
        "name": "Test Workspace for Workflow APIs"
    }
    
    response = requests.post(f"{BASE_URL}/workspaces", json=create_workspace_data)
    print_response("0. CREATE WORKSPACE", response)
    
    if response.status_code != 200:
        print("❌ Failed to create workspace. Stopping tests.")
        return
    
    workspace = response.json()
    workspace_id = workspace["id"]
    print(f"\n✅ Using workspace_id: {workspace_id}\n")
    
    # 2. Create a workflow
    create_workflow_data = {
        "workspace_id": workspace_id,
        "name": "Test LinkedIn Pipeline",
        "description": "Generate blog and image for LinkedIn",
        "target_platform": "linkedin",
        "steps": [
            {
                "order": 1,
                "name": "Generate Blog Post",
                "tool_name": "blog_generator",
                "config": {
                    "topic": "AI trends in 2025",
                    "length": "medium",
                    "tone": "professional"
                }
            },
            {
                "order": 2,
                "name": "Generate Cover Image",
                "tool_name": "image_generator",
                "config": {
                    "style": "professional",
                    "theme": "technology"
                }
            }
        ]
    }
    
    response = requests.post(f"{BASE_URL}/workflows", json=create_workflow_data)
    print_response("1. CREATE WORKFLOW", response)
    
    if response.status_code != 200:
        print("❌ Failed to create workflow. Stopping tests.")
        return
    
    workflow = response.json()
    workflow_id = workflow["id"]
    
    # 3. Get workflow details
    response = requests.get(f"{BASE_URL}/workflows/{workflow_id}")
    print_response("2. GET WORKFLOW DETAILS", response)
    
    # 4. List workflows for workspace
    response = requests.get(f"{BASE_URL}/workflows", params={"workspace_id": workspace_id})
    print_response("3. LIST WORKFLOWS", response)
    
    # 5. Update workflow
    update_data = {
        "description": "Updated: Generate blog and image with hashtags",
        "steps": [
            {
                "order": 1,
                "name": "Generate Blog",
                "tool_name": "blog_generator",
                "config": {"topic": "Updated topic"}
            },
            {
                "order": 2,
                "name": "Generate Image",
                "tool_name": "image_generator",
                "config": {"style": "modern"}
            },
            {
                "order": 3,
                "name": "Generate Hashtags",
                "tool_name": "hashtag_generator",
                "config": {"count": 5}
            }
        ]
    }
    
    response = requests.put(f"{BASE_URL}/workflows/{workflow_id}", json=update_data)
    print_response("4. UPDATE WORKFLOW", response)
    
    # 6. Run workflow (most important!)
    response = requests.post(f"{BASE_URL}/workflows/{workflow_id}/run")
    print_response("5. RUN WORKFLOW", response)
    
    if response.status_code == 200:
        job = response.json()
        job_id = job["job_id"]
        
        # 7. Get job status
        response = requests.get(f"{BASE_URL}/jobs/{job_id}")
        print_response("6. GET JOB STATUS", response)
        
        # 8. Get all jobs for workflow
        response = requests.get(f"{BASE_URL}/jobs/workflow/{workflow_id}")
        print_response("7. GET WORKFLOW JOBS", response)
    
    # 9. Try to delete workflow (should fail because job is running)
    response = requests.delete(f"{BASE_URL}/workflows/{workflow_id}")
    print_response("8. DELETE WORKFLOW (should fail)", response)
    
    # 10. Test validation: invalid tool name
    invalid_workflow = {
        "workspace_id": workspace_id,
        "name": "Invalid Workflow",
        "steps": [
            {
                "order": 1,
                "tool_name": "non_existent_tool",
                "config": {}
            }
        ]
    }
    
    response = requests.post(f"{BASE_URL}/workflows", json=invalid_workflow)
    print_response("9. VALIDATION TEST (invalid tool)", response)
    
    # 11. Test validation: non-sequential order
    invalid_workflow = {
        "workspace_id": workspace_id,
        "name": "Invalid Order Workflow",
        "steps": [
            {
                "order": 1,
                "tool_name": "blog_generator",
                "config": {}
            },
            {
                "order": 3,  # Skipped 2!
                "tool_name": "image_generator",
                "config": {}
            }
        ]
    }
    
    response = requests.post(f"{BASE_URL}/workflows", json=invalid_workflow)
    print_response("10. VALIDATION TEST (non-sequential order)", response)
    
    # 12. Test validation: no steps
    invalid_workflow = {
        "workspace_id": workspace_id,
        "name": "No Steps Workflow",
        "steps": []
    }
    
    response = requests.post(f"{BASE_URL}/workflows", json=invalid_workflow)
    print_response("11. VALIDATION TEST (no steps)", response)
    
    print("\n" + "="*60)
    print("✅ ALL TESTS COMPLETED!")
    print("="*60)

if __name__ == "__main__":
    print("🧪 Testing Workflow APIs...")
    print("Make sure the server is running: uvicorn main:app --reload")
    print()
    
    try:
        test_workflow_apis()
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Cannot connect to server. Is it running?")
        print("Start with: cd backend-python && python -m uvicorn main:app --reload")
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
