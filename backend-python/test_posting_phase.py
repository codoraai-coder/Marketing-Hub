"""
Test Suite for Posting & Distribution Phase
Tests the posting_jobs endpoints and post_to_linkedin tool
"""
import pytest
import requests
import json
from uuid import uuid4

# Configuration
BASE_URL = "http://localhost:3000/api"

# Test fixtures - replace with actual UUIDs from your database
TEST_WORKSPACE_ID = None  # Set this to a real workspace UUID
TEST_CONTENT_ID = None    # Set this to an approved content UUID
TEST_JOB_ID = None        # Will be populated during tests


class TestPostingJobsAPI:
    """Test posting jobs API endpoints"""
    
    def test_list_ready_jobs(self):
        """Test listing ready posting jobs for a workspace"""
        if not TEST_WORKSPACE_ID:
            pytest.skip("TEST_WORKSPACE_ID not configured")
        
        response = requests.get(f"{BASE_URL}/posting-jobs/workspace/{TEST_WORKSPACE_ID}/ready")
        
        assert response.status_code == 200
        jobs = response.json()
        assert isinstance(jobs, list)
        print(f"✅ Found {len(jobs)} ready jobs")
        
        if jobs:
            global TEST_JOB_ID
            TEST_JOB_ID = jobs[0]['id']
            assert 'prepared_payload' in jobs[0]
            assert jobs[0]['status'] == 'ready'
    
    def test_list_all_jobs(self):
        """Test listing all posting jobs with status filter"""
        if not TEST_WORKSPACE_ID:
            pytest.skip("TEST_WORKSPACE_ID not configured")
        
        # Test without filter
        response = requests.get(f"{BASE_URL}/posting-jobs/workspace/{TEST_WORKSPACE_ID}/all")
        assert response.status_code == 200
        all_jobs = response.json()
        assert isinstance(all_jobs, list)
        print(f"✅ Found {len(all_jobs)} total jobs")
        
        # Test with status filter
        response = requests.get(
            f"{BASE_URL}/posting-jobs/workspace/{TEST_WORKSPACE_ID}/all",
            params={"status_filter": "ready"}
        )
        assert response.status_code == 200
        ready_jobs = response.json()
        assert isinstance(ready_jobs, list)
        print(f"✅ Found {len(ready_jobs)} ready jobs (filtered)")
    
    def test_get_posting_job(self):
        """Test retrieving a specific posting job"""
        if not TEST_JOB_ID:
            pytest.skip("TEST_JOB_ID not available")
        
        response = requests.get(f"{BASE_URL}/posting-jobs/{TEST_JOB_ID}")
        
        assert response.status_code == 200
        job = response.json()
        assert job['id'] == TEST_JOB_ID
        assert 'prepared_payload' in job
        assert 'post_text' in job['prepared_payload']
        
        print(f"✅ Retrieved job: {job['id']}")
        print(f"Platform: {job['platform']}")
        print(f"Status: {job['status']}")
        print(f"Payload preview: {json.dumps(job['prepared_payload'], indent=2)[:200]}...")
    
    def test_get_nonexistent_job(self):
        """Test retrieving a non-existent posting job"""
        fake_uuid = str(uuid4())
        response = requests.get(f"{BASE_URL}/posting-jobs/{fake_uuid}")
        
        assert response.status_code == 404
        print("✅ Correctly returned 404 for non-existent job")
    
    def test_mark_job_as_failed(self):
        """Test marking a posting job as failed"""
        if not TEST_JOB_ID:
            pytest.skip("TEST_JOB_ID not available")
        
        error_message = "Test error: LinkedIn connection timeout"
        response = requests.post(
            f"{BASE_URL}/posting-jobs/{TEST_JOB_ID}/mark-failed",
            params={"error_message": error_message}
        )
        
        assert response.status_code == 200
        job = response.json()
        assert job['status'] == 'failed'
        assert job['error_message'] == error_message
        assert job['retry_count'] >= 1
        
        print(f"✅ Job marked as failed")
        print(f"Error: {job['error_message']}")
        print(f"Retry count: {job['retry_count']}")
    
    def test_retry_failed_job(self):
        """Test retrying a failed posting job"""
        if not TEST_JOB_ID:
            pytest.skip("TEST_JOB_ID not available")
        
        response = requests.post(f"{BASE_URL}/posting-jobs/{TEST_JOB_ID}/retry")
        
        assert response.status_code == 200
        job = response.json()
        assert job['status'] == 'ready'
        assert job['error_message'] is None
        
        print(f"✅ Job reset to ready status")
        print(f"Retry count preserved: {job['retry_count']}")
    
    def test_mark_job_as_posted(self):
        """Test marking a posting job as posted"""
        if not TEST_JOB_ID:
            pytest.skip("TEST_JOB_ID not available")
        
        response = requests.post(f"{BASE_URL}/posting-jobs/{TEST_JOB_ID}/mark-posted")
        
        assert response.status_code == 200
        job = response.json()
        assert job['status'] == 'posted'
        assert job['posted_at'] is not None
        
        print(f"✅ Job marked as posted at {job['posted_at']}")
    
    def test_cannot_retry_posted_job(self):
        """Test that posted jobs cannot be retried"""
        if not TEST_JOB_ID:
            pytest.skip("TEST_JOB_ID not available")
        
        response = requests.post(f"{BASE_URL}/posting-jobs/{TEST_JOB_ID}/retry")
        
        assert response.status_code == 400
        print("✅ Correctly prevented retry of posted job")


class TestPostToLinkedInTool:
    """Test the post_to_linkedin MCP tool"""
    
    def test_tool_registration(self):
        """Test that post_to_linkedin tool is registered"""
        from app.services.tool_registry import tool_registry
        
        assert tool_registry.is_tool_available("post_to_linkedin")
        print("✅ post_to_linkedin tool is registered")
    
    def test_tool_requires_approved_content(self):
        """Test that tool validates content is approved"""
        from app.services.tool_registry import tool_registry
        
        # This would need a draft content ID
        config = {
            "content_id": "some-draft-content-id",
            "workspace_id": TEST_WORKSPACE_ID or "test-workspace"
        }
        
        # Tool should raise error for non-approved content
        # Note: This test requires actual database setup
        print("⚠️ Manual test: Tool should reject draft/non-approved content")
    
    def test_tool_creates_posting_job(self):
        """Test that tool creates posting_job record"""
        # This requires an actual approved content record
        # and workflow execution
        print("⚠️ Manual test: Run a workflow with post_to_linkedin step")


class TestContentLifecycle:
    """Test content status updates during posting"""
    
    def test_content_status_updates_when_posted(self):
        """Test that content.status updates to 'posted' when job is marked posted"""
        if not TEST_CONTENT_ID:
            pytest.skip("TEST_CONTENT_ID not configured")
        
        # Get content before
        response = requests.get(f"{BASE_URL}/content/{TEST_CONTENT_ID}")
        if response.status_code == 200:
            content_before = response.json()
            print(f"Content status before: {content_before.get('status')}")
        
        # Mark job as posted (this also updates content)
        # Then verify content status changed
        print("⚠️ Manual test: Verify content.status → 'posted' after mark-posted")


def print_test_setup_instructions():
    """Print instructions for setting up test environment"""
    print("\n" + "="*70)
    print("🧪 POSTING PHASE TEST SETUP INSTRUCTIONS")
    print("="*70)
    print("\n1. Apply the migration:")
    print("   cat migrations/003_add_posting_jobs.sql | Supabase SQL Editor")
    print("\n2. Start the backend:")
    print("   python main.py")
    print("\n3. Create test data:")
    print("   - Create a workspace")
    print("   - Create a workflow with caption_generator")
    print("   - Run the workflow")
    print("   - Approve the generated content")
    print("   - Add post_to_linkedin step to workflow")
    print("   - Run workflow again")
    print("\n4. Update test configuration:")
    print("   - Set TEST_WORKSPACE_ID in this file")
    print("   - Set TEST_CONTENT_ID in this file")
    print("\n5. Run tests:")
    print("   pytest test_posting_phase.py -v")
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    print_test_setup_instructions()
    
    # Run a basic connectivity test
    print("🔍 Testing API connectivity...")
    try:
        response = requests.get(f"{BASE_URL.replace('/api', '')}/health")
        if response.status_code == 200:
            print("✅ Backend is running!")
            print(f"Response: {response.json()}")
        else:
            print(f"⚠️ Backend returned status {response.status_code}")
    except Exception as e:
        print(f"❌ Cannot connect to backend: {e}")
        print(f"Make sure backend is running on {BASE_URL.replace('/api', '')}")
