#!/usr/bin/env python3
"""
Hash-based backend deletion script for StilBAR compounds
Uses hash-based identification for consistent compound management
"""
import sys
import json
from hash_compound_manager import HashCompoundManager

def delete_compounds_by_hashes(hash_keys: list) -> dict:
    """
    Delete compounds by hash keys using the hash-based manager
    """
    print(f"🔍 Hash Backend: Attempting to delete hashes: {hash_keys}")
    
    try:
        manager = HashCompoundManager()
        result = manager.delete_compounds(hash_keys)
        
        print(f"🔍 Hash Backend: Deletion result:")
        print(f"  Success: {result['success']}")
        print(f"  Deleted count: {result['deleted_count']}")
        print(f"  Errors: {result['errors']}")
        
        for deleted in result['deleted_compounds']:
            print(f"  Deleted: {deleted['hash']} - {deleted['name']} ({deleted['stilbar']})")
        
        return result
        
    except Exception as e:
        return {
            'success': False,
            'deleted_count': 0,
            'errors': [f"Exception: {str(e)}"],
            'deleted_compounds': []
        }

def delete_compounds_by_stilbars(stilbar_codes: list) -> dict:
    """
    Delete compounds by StilBAR codes (converts to hashes first)
    """
    print(f"🔍 Hash Backend: Converting StilBAR codes to hashes: {stilbar_codes}")
    
    try:
        manager = HashCompoundManager()
        hash_keys = []
        conversion_errors = []
        
        for stilbar in stilbar_codes:
            compound = manager.get_compound_by_stilbar(stilbar)
            if compound:
                hash_keys.append(compound['hash'])
                print(f"  {stilbar} → {compound['hash']}")
            else:
                conversion_errors.append(f"StilBAR code not found: {stilbar}")
        
        if conversion_errors:
            return {
                'success': False,
                'deleted_count': 0,
                'errors': conversion_errors,
                'deleted_compounds': []
            }
        
        if not hash_keys:
            return {
                'success': False,
                'deleted_count': 0,
                'errors': ['No valid StilBAR codes provided'],
                'deleted_compounds': []
            }
        
        # Proceed with hash-based deletion
        return delete_compounds_by_hashes(hash_keys)
        
    except Exception as e:
        return {
            'success': False,
            'deleted_count': 0,
            'errors': [f"Exception: {str(e)}"],
            'deleted_compounds': []
        }

def main():
    """Main function for command line usage"""
    if len(sys.argv) < 3:
        print("Usage:")
        print("  python hash_deletion_backend.py --hashes <hash1> [hash2] ...")
        print("  python hash_deletion_backend.py --stilbars <stilbar1> [stilbar2] ...")
        print()
        print("Examples:")
        print("  python hash_deletion_backend.py --hashes 2cb53c72 44bd7ae6")
        print("  python hash_deletion_backend.py --stilbars \"H–77–H\" \"H\"")
        return
    
    mode = sys.argv[1]
    identifiers = sys.argv[2:]
    
    if mode == '--hashes':
        result = delete_compounds_by_hashes(identifiers)
    elif mode == '--stilbars':
        result = delete_compounds_by_stilbars(identifiers)
    else:
        print(f"Invalid mode: {mode}. Use --hashes or --stilbars")
        return
    
    # Print result as JSON for easy parsing
    print("🔍 Hash Backend: RESULT:")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()