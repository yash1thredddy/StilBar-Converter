"""
Fixed SMILES Generator - now uses HashCompoundManager as single source of truth
"""
import re
from typing import Dict, List, Tuple, Optional
from hash_compound_manager import HashCompoundManager

class FixedSMILESGenerator:
    """Fixed SMILES generator that uses HashCompoundManager as single data source"""
    
    def __init__(self, hash_manager=None):
        if hash_manager:
            self.hash_manager = hash_manager
        else:
            self.hash_manager = HashCompoundManager()
    
    def reload_database(self):
        """Reload database from hash manager"""
        self.hash_manager.load_compounds()
    
    def generate_smiles(self, input_code: str) -> Tuple[str, Dict]:
        """
        Generate SMILES for any input (barcode or compound number)
        Returns (smiles_string, metadata_dict) for compatibility
        """
        # Clean input: remove all spaces and normalize
        clean_code = input_code.strip().replace(' ', '')
        
        # Normalize dashes: convert regular hyphens (-) to en-dashes (–) for compatibility
        normalized_code = clean_code.replace('-', '–')
        
        # Try to find by StilBAR code first
        compound = self.hash_manager.get_compound_by_stilbar(normalized_code)
        if compound:
            return compound['smiles'], {
                'found_method': 'stilbar_lookup',
                'compound_name': compound['name'],
                'stilbar_code': compound['stilbar'],
                'source': 'hash_manager'
            }
        
        # Try original input too
        if clean_code != normalized_code:
            compound = self.hash_manager.get_compound_by_stilbar(clean_code)
            if compound:
                return compound['smiles'], {
                    'found_method': 'stilbar_lookup_original',
                    'compound_name': compound['name'],
                    'stilbar_code': compound['stilbar'],
                    'source': 'hash_manager'
                }
        
        # Try by compound number (if it's numeric)
        if clean_code.isdigit():
            all_compounds = self.hash_manager.get_all_compounds()
            try:
                compound_num = int(clean_code)
                if 1 <= compound_num <= len(all_compounds):
                    compound = all_compounds[compound_num - 1]  # 0-indexed
                    return compound['smiles'], {
                        'found_method': 'compound_number',
                        'compound_name': compound['name'],
                        'stilbar_code': compound['stilbar'],
                        'compound_number': compound_num,
                        'source': 'hash_manager'
                    }
            except (ValueError, IndexError):
                pass
        
        # Not found
        return None, {
            'found_method': 'not_found',
            'input_code': input_code,
            'cleaned_code': clean_code,
            'normalized_code': normalized_code,
            'source': 'hash_manager'
        }
    
    def get_all_compound_numbers(self) -> List[int]:
        """Get all available compound numbers"""
        all_compounds = self.hash_manager.get_all_compounds()
        return list(range(1, len(all_compounds) + 1))
    
    def get_all_barcodes(self) -> List[str]:
        """Get all available StilBAR codes"""
        all_compounds = self.hash_manager.get_all_compounds()
        return [comp['stilbar'] for comp in all_compounds if comp['stilbar']]
    
    def get_compound_info(self, compound_number: int) -> Optional[Dict]:
        """Get compound info by number"""
        all_compounds = self.hash_manager.get_all_compounds()
        if 1 <= compound_number <= len(all_compounds):
            compound = all_compounds[compound_number - 1]
            return {
                'number': compound_number,
                'name': compound['name'],
                'barcode': compound['stilbar'],
                'smiles': compound['smiles']
            }
        return None