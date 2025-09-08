#!/usr/bin/env python3
"""
Configuration file for StilBAR application
Choose between CSV or Supabase backend
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Database backend configuration
USE_SUPABASE = os.getenv('USE_SUPABASE', 'true').lower() == 'true'

def get_compound_manager():
    """Get the appropriate compound manager based on configuration"""
    if USE_SUPABASE:
        try:
            from supabase_compound_manager import SupabaseCompoundManager
            return SupabaseCompoundManager()
        except ImportError as e:
            print(f"❌ Supabase not available: {e}")
            print("🔄 Falling back to CSV backend...")
            from hash_compound_manager import HashCompoundManager
            return HashCompoundManager()
    else:
        from hash_compound_manager import HashCompoundManager
        return HashCompoundManager()

# For backwards compatibility
def create_compound_manager():
    """Create compound manager (alias for get_compound_manager)"""
    return get_compound_manager()