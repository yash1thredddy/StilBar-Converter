#!/usr/bin/env python3
"""
Simple test for direct deletion functionality
"""
from hash_compound_manager import HashCompoundManager

def test_simple_delete():
    # Initialize manager
    manager = HashCompoundManager()
    
    # Show available compounds
    compounds = manager.get_all_compounds()
    print(f"📊 Total compounds: {len(compounds)}")
    
    # Show first few compounds
    print("\n🔍 First 5 compounds:")
    for i, comp in enumerate(compounds[:5]):
        print(f"  {i+1}. {comp['hash'][:8]} - {comp['name'][:40]}... ({comp['stilbar']})")
    
    # Test deletion of first compound
    if compounds:
        test_hash = compounds[0]['hash']
        test_name = compounds[0]['name']
        
        print(f"\n🗑️ Testing deletion of: {test_name} (Hash: {test_hash[:8]})")
        
        result = manager.delete_compounds([test_hash])
        print(f"📊 Deletion result: {result}")
        
        # Check new count
        new_compounds = manager.get_all_compounds()
        print(f"📊 New compound count: {len(new_compounds)}")

if __name__ == "__main__":
    test_simple_delete()