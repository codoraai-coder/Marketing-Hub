"""
Test X (Twitter) API Connection
Run: python test_x_connection.py
"""
import os
from dotenv import load_dotenv
import tweepy

# Load environment variables
load_dotenv()

def test_x_credentials():
    """Test X API credentials by fetching authenticated user info"""
    
    # Get credentials from .env
    api_key = os.getenv("X_API_KEY")
    api_secret = os.getenv("X_API_SECRET")
    access_token = os.getenv("X_ACCESS_TOKEN")
    access_token_secret = os.getenv("X_ACCESS_TOKEN_SECRET")
    bearer_token = os.getenv("X_BEARER_TOKEN")
    
    # Check if credentials exist
    print("=" * 50)
    print("🔍 Checking X API Credentials...")
    print("=" * 50)
    
    missing = []
    if not api_key:
        missing.append("X_API_KEY")
    if not api_secret:
        missing.append("X_API_SECRET")
    if not access_token:
        missing.append("X_ACCESS_TOKEN")
    if not access_token_secret:
        missing.append("X_ACCESS_TOKEN_SECRET")
    
    if missing:
        print(f"❌ Missing credentials: {', '.join(missing)}")
        print("   Add them to your .env file")
        return False
    
    print("✅ All credentials found in .env")
    print()
    
    # Test OAuth 1.0a (for posting)
    print("🔐 Testing OAuth 1.0a authentication...")
    try:
        auth = tweepy.OAuth1UserHandler(
            api_key, api_secret,
            access_token, access_token_secret
        )
        api = tweepy.API(auth)
        
        # Verify credentials by getting user info
        user = api.verify_credentials()
        print(f"✅ OAuth 1.0a SUCCESS!")
        print(f"   Connected as: @{user.screen_name}")
        print(f"   Name: {user.name}")
        print(f"   Followers: {user.followers_count}")
        print()
        
    except tweepy.TweepyException as e:
        print(f"❌ OAuth 1.0a FAILED: {e}")
        return False
    
    # Test OAuth 2.0 Bearer Token (for reading)
    if bearer_token:
        print("🔐 Testing OAuth 2.0 Bearer Token...")
        try:
            client = tweepy.Client(
                bearer_token=bearer_token,
                consumer_key=api_key,
                consumer_secret=api_secret,
                access_token=access_token,
                access_token_secret=access_token_secret
            )
            # Get authenticated user
            user_response = client.get_me()
            if user_response.data:
                print(f"✅ Bearer Token SUCCESS!")
            else:
                print("⚠️  Bearer Token works but returned no data")
        except tweepy.TweepyException as e:
            print(f"⚠️  Bearer Token test failed (optional): {e}")
    else:
        print("ℹ️  X_BEARER_TOKEN not set (optional for posting)")
    
    print()
    print("=" * 50)
    print("🎉 X API CONNECTION TEST PASSED!")
    print("=" * 50)
    print()
    print("You can now use the post_to_x tool in workflows.")
    
    return True


if __name__ == "__main__":
    test_x_credentials()
