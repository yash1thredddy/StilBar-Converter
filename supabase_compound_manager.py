#!/usr/bin/env python3
"""
Supabase-based compound management system for StilBAR compounds
Drop-in replacement for HashCompoundManager that uses Supabase
"""
from typing import Dict, List, Optional
from supabase_adapter import SupabaseAdapter

class SupabaseCompoundManager:
    """Manage compounds using Supabase database - drop-in replacement for HashCompoundManager"""
    
    def __init__(self):
        """Initialize Supabase compound manager"""
        self.supabase = SupabaseAdapter()
    
    def load_compounds(self):
        """Load compounds from database (no-op for Supabase as it's always live)"""
        # This method exists for compatibility with CSV-based system
        # In Supabase, data is always fresh, so this is a no-op
        pass
    
    def get_all_compounds(self) -> List[Dict]:
        """Get all compounds from database"""
        return self.supabase.get_all_compounds()
    
    def get_compound_by_stilbar(self, stilbar_code: str) -> Optional[Dict]:
        """Get compound by StilBAR code"""
        return self.supabase.get_compound_by_stilbar(stilbar_code)
    
    def get_compound_by_hash(self, hash_key: str) -> Optional[Dict]:
        """Get compound by hash ID"""
        return self.supabase.get_compound_by_hash(hash_key)
    
    def add_compound(self, name: str, stilbar_code: str, smiles: str) -> str:
        """Add new compound and return its hash"""
        success, result = self.supabase.add_compound(name, stilbar_code, smiles)
        if success:
            return result  # This is the hash_id
        else:
            raise ValueError(result)  # This is the error message
    
    def delete_compounds(self, hash_keys: List[str]) -> Dict:
        """Delete compounds by hash keys"""
        return self.supabase.delete_compounds(hash_keys)
    
    def update_compound(self, hash_id: str, name: str = None, stilbar_code: str = None, smiles: str = None) -> bool:
        """Update existing compound"""
        success, message = self.supabase.update_compound(hash_id, name, stilbar_code, smiles)
        if not success:
            raise ValueError(message)
        return success
    
    def search_compounds(self, search_term: str) -> List[Dict]:
        """Search compounds by name or StilBAR code"""
        return self.supabase.search_compounds(search_term)
    
    def get_stats(self) -> Dict:
        """Get database statistics"""
        return self.supabase.get_stats()
    
    def is_connected(self) -> bool:
        """Check if database is connected"""
        return self.supabase.is_connected()
    
    # Additional convenience methods
    def generate_hash(self, stilbar_code: str, compound_name: str = '') -> str:
        """Generate hash for compound (for compatibility)"""
        return self.supabase.generate_hash(stilbar_code, compound_name)