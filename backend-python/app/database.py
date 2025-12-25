from supabase import create_client, Client
import os
from dotenv import load_dotenv

load_dotenv()

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY")

# Create Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


# Dependency to get Supabase client
def get_supabase() -> Client:
    return supabase
