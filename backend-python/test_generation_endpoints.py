"""
Test the simplified generation endpoints
"""
import requests
import time

BASE_URL = "http://localhost:8000"


def test_generate_caption():
    """Test POST /api/v1/generate/caption endpoint"""
    print("\n=== Testing Caption Generation ===")
    
    response = requests.post(
        f"{BASE_URL}/api/v1/generate/caption",
        json={
            "topic": "The Future of AI",
            "platform": "linkedin",
            "tone": "professional",
            "include_emojis": True,
            "include_hashtags": True
        }
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    
    assert "id" in data, "Response missing 'id' field"
    assert "caption" in data, "Response missing 'caption' field"
    assert "platform" in data, "Response missing 'platform' field"
    assert "created_at" in data, "Response missing 'created_at' field"
    
    print("✅ Caption generation test passed!")
    return data


def test_generate_hashtags():
    """Test POST /api/v1/generate/hashtags endpoint"""
    print("\n=== Testing Hashtag Generation ===")
    
    response = requests.post(
        f"{BASE_URL}/api/v1/generate/hashtags",
        json={
            "topic": "Artificial Intelligence in Healthcare",
            "count": 5,
            "platform": "linkedin"
        }
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    
    assert "id" in data, "Response missing 'id' field"
    assert "hashtags" in data, "Response missing 'hashtags' field"
    assert "count" in data, "Response missing 'count' field"
    assert isinstance(data["hashtags"], list), "hashtags should be a list"
    
    print("✅ Hashtag generation test passed!")
    return data


def test_optimize_content():
    """Test POST /api/v1/generate/optimize endpoint"""
    print("\n=== Testing Content Optimization ===")
    
    original_content = "AI is changing the world. Companies are using it. It's important for business."
    
    response = requests.post(
        f"{BASE_URL}/api/v1/generate/optimize",
        json={
            "content": original_content,
            "goal": "engagement",
            "audience": "tech professionals",
            "platform": "linkedin"
        }
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    
    assert "id" in data, "Response missing 'id' field"
    assert "original" in data, "Response missing 'original' field"
    assert "optimized" in data, "Response missing 'optimized' field"
    assert "goal" in data, "Response missing 'goal' field"
    
    print("✅ Content optimization test passed!")
    return data


def test_generate_blog_post():
    """Test POST /api/v1/generate/blog_post endpoint"""
    print("\n=== Testing Blog Post Generation ===")
    
    response = requests.post(
        f"{BASE_URL}/api/v1/generate/blog_post",
        json={"topic": "The Future of AI"}
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    
    assert "id" in data, "Response missing 'id' field"
    assert "topic" in data, "Response missing 'topic' field"
    assert "docx_url" in data, "Response missing 'docx_url' field"
    assert "cover_url" in data, "Response missing 'cover_url' field"
    assert "created_at" in data, "Response missing 'created_at' field"
    
    print("✅ Blog post generation test passed!")
    return data


def test_validation_errors():
    """Test validation errors for missing/empty fields"""
    print("\n=== Testing Validation Errors ===")
    
    # Test missing topic for caption
    response = requests.post(
        f"{BASE_URL}/api/v1/generate/caption",
        json={}
    )
    print(f"Missing topic (caption) - Status Code: {response.status_code}")
    assert response.status_code == 422, f"Expected 422, got {response.status_code}"
    
    # Test empty topic for hashtags
    response = requests.post(
        f"{BASE_URL}/api/v1/generate/hashtags",
        json={"topic": ""}
    )
    print(f"Empty topic (hashtags) - Status Code: {response.status_code}")
    assert response.status_code == 422, f"Expected 422, got {response.status_code}"
    
    # Test missing content for optimize
    response = requests.post(
        f"{BASE_URL}/api/v1/generate/optimize",
        json={}
    )
    print(f"Missing content (optimize) - Status Code: {response.status_code}")
    assert response.status_code == 422, f"Expected 422, got {response.status_code}"
    
    print("✅ Validation error tests passed!")


if __name__ == "__main__":
    try:
        # Test validation first
        test_validation_errors()
        
        # Test caption generation
        test_generate_caption()
        
        # Test hashtag generation
        test_generate_hashtags()
        
        # Test content optimization
        test_optimize_content()
        
        # Test blog post generation
        test_generate_blog_post()
        
        print("\n" + "="*50)
        print("🎉 All tests passed successfully!")
        print("="*50)
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        exit(1)
    except requests.exceptions.ConnectionError:
        print("\n❌ Could not connect to server. Make sure the backend is running on port 8000")
        exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        exit(1)
