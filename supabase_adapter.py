#!/usr/bin/env python3
"""
Supabase Database Adapter for StilBAR Compounds
Handles all database operations using Supabase PostgreSQL
"""
import os
import hashlib
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False

class SupabaseAdapter:
    """Supabase database adapter for StilBAR compounds"""
    
    def __init__(self):
        """Initialize Supabase client"""
        self.client: Optional[Client] = None
        self.table_name = "stilbar_compounds"
        
        if SUPABASE_AVAILABLE:
            self._initialize_client()
        else:
            st.error("⚠️ Supabase not installed. Run: pip install supabase")
    
    def _initialize_client(self):
        """Initialize Supabase client with credentials"""
        try:
            # Get credentials from environment or Streamlit secrets
            supabase_url = self._get_credential("SUPABASE_URL")
            supabase_key = self._get_credential("SUPABASE_ANON_KEY")
            
            if supabase_url and supabase_key:
                self.client = create_client(supabase_url, supabase_key)
                print(f"✅ Supabase connected to: {supabase_url}")
            else:
                st.error("❌ Supabase credentials not found. Please set SUPABASE_URL and SUPABASE_ANON_KEY")
                
        except Exception as e:
            st.error(f"❌ Failed to initialize Supabase: {e}")
    
    def _get_credential(self, key: str) -> Optional[str]:
        """Get credential from environment or Streamlit secrets"""
        # Try environment variable first
        value = os.getenv(key)
        if value:
            return value
        
        # Try Streamlit secrets
        try:
            return st.secrets[key]
        except (KeyError, FileNotFoundError):
            return None
    
    def generate_hash(self, stilbar_code: str, compound_name: str = '') -> str:
        """Generate a unique hash from StilBAR code and compound name"""
        clean_stilbar = stilbar_code.strip().replace(' ', '').replace('-', '–')
        combined = f"{clean_stilbar}|{compound_name.strip()}"
        hash_obj = hashlib.sha256(combined.encode('utf-8'))
        return hash_obj.hexdigest()[:16]  # Longer hash for better uniqueness
    
    def get_all_compounds(self) -> List[Dict]:
        """Get all compounds from database"""
        if not self.client:
            return []
        
        try:
            result = self.client.table(self.table_name).select("*").order("created_at").execute()
            compounds = []
            
            for row in result.data:
                compounds.append({
                    'hash': row['hash_id'],
                    'name': row['compound_name'],
                    'stilbar': row['stilbar_code'],
                    'smiles': row['smiles'],
                    'created_at': row.get('created_at'),
                    'updated_at': row.get('updated_at')
                })
            
            return compounds
            
        except Exception as e:
            st.error(f"❌ Error fetching compounds: {e}")
            return []
    
    def get_compound_by_stilbar(self, stilbar_code: str) -> Optional[Dict]:
        """Get compound by StilBAR code"""
        if not self.client:
            return None
        
        try:
            result = self.client.table(self.table_name).select("*").eq("stilbar_code", stilbar_code).execute()
            
            if result.data:
                row = result.data[0]
                return {
                    'hash': row['hash_id'],
                    'name': row['compound_name'],
                    'stilbar': row['stilbar_code'],
                    'smiles': row['smiles'],
                    'created_at': row.get('created_at'),
                    'updated_at': row.get('updated_at')
                }
            
            return None
            
        except Exception as e:
            st.error(f"❌ Error fetching compound by StilBAR: {e}")
            return None
    
    def get_compound_by_hash(self, hash_id: str) -> Optional[Dict]:
        """Get compound by hash ID"""
        if not self.client:
            return None
        
        try:
            result = self.client.table(self.table_name).select("*").eq("hash_id", hash_id).execute()
            
            if result.data:
                row = result.data[0]
                return {
                    'hash': row['hash_id'],
                    'name': row['compound_name'],
                    'stilbar': row['stilbar_code'],
                    'smiles': row['smiles'],
                    'created_at': row.get('created_at'),
                    'updated_at': row.get('updated_at')
                }
            
            return None
            
        except Exception as e:
            st.error(f"❌ Error fetching compound by hash: {e}")
            return None
    
    def add_compound(self, name: str, stilbar_code: str, smiles: str) -> Tuple[bool, str]:
        """Add new compound to database"""
        if not self.client:
            return False, "Database not connected"
        
        try:
            # Generate hash
            hash_id = self.generate_hash(stilbar_code, name)
            
            # Check if already exists
            existing = self.get_compound_by_stilbar(stilbar_code)
            if existing:
                return False, f"Compound with StilBAR code '{stilbar_code}' already exists"
            
            # Insert new compound
            data = {
                'hash_id': hash_id,
                'compound_name': name,
                'stilbar_code': stilbar_code,
                'smiles': smiles,
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }
            
            result = self.client.table(self.table_name).insert(data).execute()
            
            if result.data:
                return True, hash_id
            else:
                return False, "Failed to insert compound"
                
        except Exception as e:
            return False, f"Error adding compound: {e}"
    
    def delete_compounds(self, hash_ids: List[str]) -> Dict:
        """Delete compounds by hash IDs"""
        if not self.client:
            return {
                'success': False,
                'deleted_count': 0,
                'deleted_compounds': [],
                'errors': ['Database not connected']
            }
        
        result = {
            'success': False,
            'deleted_count': 0,
            'deleted_compounds': [],
            'errors': []
        }
        
        try:
            # Get compounds to delete first (for tracking)
            compounds_to_delete = []
            for hash_id in hash_ids:
                compound = self.get_compound_by_hash(hash_id)
                if compound:
                    compounds_to_delete.append(compound)
                else:
                    result['errors'].append(f"Hash not found: {hash_id}")
            
            if not compounds_to_delete:
                result['errors'].append("No valid compounds found to delete")
                return result
            
            # Perform deletion
            for compound in compounds_to_delete:
                try:
                    delete_result = self.client.table(self.table_name).delete().eq("hash_id", compound['hash']).execute()
                    
                    if delete_result.data:
                        result['deleted_compounds'].append({
                            'hash': compound['hash'],
                            'name': compound['name'],
                            'stilbar': compound['stilbar']
                        })
                        result['deleted_count'] += 1
                    else:
                        result['errors'].append(f"Failed to delete: {compound['name']}")
                        
                except Exception as e:
                    result['errors'].append(f"Error deleting {compound['name']}: {e}")
            
            result['success'] = result['deleted_count'] > 0
            return result
            
        except Exception as e:
            result['errors'].append(f"Exception during deletion: {str(e)}")
            return result
    
    def update_compound(self, hash_id: str, name: str = None, stilbar_code: str = None, smiles: str = None) -> Tuple[bool, str]:
        """Update existing compound"""
        if not self.client:
            return False, "Database not connected"
        
        try:
            # Build update data
            update_data = {'updated_at': datetime.utcnow().isoformat()}
            
            if name is not None:
                update_data['compound_name'] = name
            if stilbar_code is not None:
                update_data['stilbar_code'] = stilbar_code
            if smiles is not None:
                update_data['smiles'] = smiles
            
            result = self.client.table(self.table_name).update(update_data).eq("hash_id", hash_id).execute()
            
            if result.data:
                return True, "Compound updated successfully"
            else:
                return False, "No compound found with that hash ID"
                
        except Exception as e:
            return False, f"Error updating compound: {e}"
    
    def search_compounds(self, search_term: str) -> List[Dict]:
        """Search compounds by name or StilBAR code"""
        if not self.client:
            return []
        
        try:
            # Search in both compound_name and stilbar_code
            result = self.client.table(self.table_name).select("*").or_(
                f"compound_name.ilike.%{search_term}%,stilbar_code.ilike.%{search_term}%"
            ).execute()
            
            compounds = []
            for row in result.data:
                compounds.append({
                    'hash': row['hash_id'],
                    'name': row['compound_name'],
                    'stilbar': row['stilbar_code'],
                    'smiles': row['smiles'],
                    'created_at': row.get('created_at'),
                    'updated_at': row.get('updated_at')
                })
            
            return compounds
            
        except Exception as e:
            st.error(f"❌ Error searching compounds: {e}")
            return []
    
    def get_stats(self) -> Dict:
        """Get database statistics"""
        if not self.client:
            return {'total_compounds': 0, 'compounds_with_stilbar': 0, 'compounds_without_stilbar': 0}
        
        try:
            # Get total count
            total_result = self.client.table(self.table_name).select("count", count="exact").execute()
            total_count = total_result.count
            
            # Get count with StilBAR codes
            with_stilbar_result = self.client.table(self.table_name).select("count", count="exact").neq("stilbar_code", "").execute()
            with_stilbar_count = with_stilbar_result.count
            
            return {
                'total_compounds': total_count,
                'compounds_with_stilbar': with_stilbar_count,
                'compounds_without_stilbar': total_count - with_stilbar_count
            }
            
        except Exception as e:
            st.error(f"❌ Error getting stats: {e}")
            return {'total_compounds': 0, 'compounds_with_stilbar': 0, 'compounds_without_stilbar': 0}
    
    def is_connected(self) -> bool:
        """Check if database is connected"""
        return self.client is not None and SUPABASE_AVAILABLE