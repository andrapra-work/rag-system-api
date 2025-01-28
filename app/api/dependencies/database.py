from fastapi import Depends
from app.services.supabase import SupabaseService
from functools import lru_cache

@lru_cache()
def get_supabase_service() -> SupabaseService:
    return SupabaseService()

async def get_db(
    supabase_service: SupabaseService = Depends(get_supabase_service)
) -> SupabaseService:
    return supabase_service