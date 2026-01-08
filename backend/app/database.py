from supabase import create_client, Client
from app.config import get_settings

settings = get_settings()

supabase: Client = create_client(
    settings.supabase_url,
    settings.supabase_publishable_key
)

supabase_admin: Client = create_client(
    settings.supabase_url,
    settings.supabase_secret_key
)

def get_supabase() -> Client:
    """Dependency to get Supabase client with publishable key"""
    return supabase

def get_supabase_admin() -> Client:
    """Dependency to get Supabase admin client with secret key (bypasses RLS)"""
    return supabase_admin