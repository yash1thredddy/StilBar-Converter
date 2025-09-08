#!/usr/bin/env python3
"""
Supabase-only SMILES Generator - Clean and simple
No CSV fallbacks, pure database-driven approach
"""
import re
from typing import Dict, List, Tuple, Optional
from supabase_compound_manager import SupabaseCompoundManager

class SupabaseSMILESGenerator:
    """Clean SMILES generator that works exclusively with Supabase"""
    
    def __init__(self):
        """Initialize with Supabase compound manager"""
        self.compound_manager = SupabaseCompoundManager()
    
    def generate_smiles(self, input_code: str) -> Tuple[str, Dict]:
        """
        Generate SMILES for any input (barcode or compound number)
        Returns (smiles_string, metadata_dict)
        """
        if not self.compound_manager.is_connected():
            return None, {
                'error': 'Database not connected',
                'input_code': input_code,
                'source': 'supabase_error'
            }
        
        # Clean input: remove all spaces and normalize
        clean_code = input_code.strip().replace(' ', '')
        
        # Normalize dashes: convert regular hyphens (-) to en-dashes (–) for compatibility
        normalized_code = clean_code.replace('-', '–')
        
        # Try to find by StilBAR code first
        compound = self.compound_manager.get_compound_by_stilbar(normalized_code)
        if compound:
            return compound['smiles'], {
                'found_method': 'stilbar_lookup',
                'compound_name': compound['name'],
                'stilbar_code': compound['stilbar'],
                'source': 'supabase',
                'hash_id': compound['hash']
            }
        
        # Try original input too
        if clean_code != normalized_code:
            compound = self.compound_manager.get_compound_by_stilbar(clean_code)
            if compound:
                return compound['smiles'], {
                    'found_method': 'stilbar_lookup_original',
                    'compound_name': compound['name'],
                    'stilbar_code': compound['stilbar'],
                    'source': 'supabase',
                    'hash_id': compound['hash']
                }
        
        # Try by compound number (if it's numeric)
        if clean_code.isdigit():
            all_compounds = self.compound_manager.get_all_compounds()
            try:
                compound_num = int(clean_code)
                if 1 <= compound_num <= len(all_compounds):
                    compound = all_compounds[compound_num - 1]  # 0-indexed
                    return compound['smiles'], {
                        'found_method': 'compound_number',
                        'compound_name': compound['name'],
                        'stilbar_code': compound['stilbar'],
                        'compound_number': compound_num,
                        'source': 'supabase',
                        'hash_id': compound['hash']
                    }
            except (ValueError, IndexError):
                pass
        
        # Try by hash ID (if it looks like a hash)
        if len(clean_code) == 16 and all(c in '0123456789abcdef' for c in clean_code.lower()):
            compound = self.compound_manager.get_compound_by_hash(clean_code)
            if compound:
                return compound['smiles'], {
                    'found_method': 'hash_lookup',
                    'compound_name': compound['name'],
                    'stilbar_code': compound['stilbar'],
                    'source': 'supabase',
                    'hash_id': compound['hash']
                }
        
        # Not found
        return None, {
            'found_method': 'not_found',
            'input_code': input_code,
            'cleaned_code': clean_code,
            'normalized_code': normalized_code,
            'source': 'supabase'
        }
    
    def get_all_compound_numbers(self) -> List[int]:
        """Get all available compound numbers (sequential IDs for UI)"""
        all_compounds = self.compound_manager.get_all_compounds()
        return list(range(1, len(all_compounds) + 1))
    
    def get_all_barcodes(self) -> List[str]:
        """Get all available StilBAR codes"""
        all_compounds = self.compound_manager.get_all_compounds()
        return [comp['stilbar'] for comp in all_compounds if comp['stilbar']]
    
    def get_compound_info(self, compound_number: int) -> Optional[Dict]:
        """Get compound info by sequential number"""
        all_compounds = self.compound_manager.get_all_compounds()
        if 1 <= compound_number <= len(all_compounds):
            compound = all_compounds[compound_number - 1]
            return {
                'number': compound_number,
                'hash_id': compound['hash'],
                'name': compound['name'],
                'barcode': compound['stilbar'],
                'smiles': compound['smiles']
            }
        return None
    
    def add_compound(self, name: str, stilbar_code: str, smiles: str) -> Tuple[bool, str]:
        """Add new compound to database"""
        try:
            hash_id = self.compound_manager.add_compound(name, stilbar_code, smiles)
            return True, hash_id
        except ValueError as e:
            return False, str(e)
    
    def delete_compounds(self, hash_ids: List[str]) -> Dict:
        """Delete compounds by hash IDs"""
        return self.compound_manager.delete_compounds(hash_ids)
    
    def search_compounds(self, search_term: str) -> List[Dict]:
        """Search compounds by name or StilBAR code"""
        return self.compound_manager.search_compounds(search_term)
    
    def get_stats(self) -> Dict:
        """Get database statistics"""
        return self.compound_manager.get_stats()
    
    def is_connected(self) -> bool:
        """Check if database is connected"""
        return self.compound_manager.is_connected()
    
    def reload_database(self):
        """Reload database (no-op for Supabase as it's always live)"""
        # This method exists for compatibility
        # In Supabase, data is always fresh, so this is a no-op
        pass