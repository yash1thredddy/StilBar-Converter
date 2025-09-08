#!/usr/bin/env python3
"""
Test script to verify Supabase connection and add compound functionality
"""
import sys
from supabase_smiles_generator import SupabaseSMILESGenerator

def test_connection():
    """Test basic Supabase connection"""
    print("🔍 Testing Supabase connection...")
    
    generator = SupabaseSMILESGenerator()
    
    if not generator.is_connected():
        print("❌ Supabase connection failed!")
        print("   Check your .env file or secrets.toml")
        return False
    
    print("✅ Supabase connected successfully!")
    return True

def test_database_read():
    """Test reading from database"""
    print("📊 Testing database read...")
    
    generator = SupabaseSMILESGenerator()
    compounds = generator.compound_manager.get_all_compounds()
    
    print(f"✅ Found {len(compounds)} compounds in database")
    
    if compounds:
        sample = compounds[0]
        print(f"📝 Sample compound: {sample['name']}")
        print(f"   StilBAR: {sample['stilbar']}")
        print(f"   Hash: {sample['hash']}")
    
    return len(compounds) > 0

def test_compound_lookup():
    """Test compound lookup"""
    print("🔍 Testing compound lookup...")
    
    generator = SupabaseSMILESGenerator()
    
    # Test with a known compound
    test_stilbar = "H–77–H"
    smiles, metadata = generator.generate_smiles(test_stilbar)
    
    if smiles:
        print(f"✅ Found compound for '{test_stilbar}':")
        print(f"   SMILES: {smiles[:50]}...")
        print(f"   Method: {metadata.get('found_method')}")
        print(f"   Name: {metadata.get('compound_name')}")
        return True
    else:
        print(f"❌ Could not find compound for '{test_stilbar}'")
        return False

def test_add_compound():
    """Test adding a new compound"""
    print("➕ Testing compound addition...")
    
    generator = SupabaseSMILESGenerator()
    
    # Test compound data
    test_name = "TEST_Compound_DELETE_ME"
    test_stilbar = "TEST-CODE-DELETE"
    test_smiles = "O"  # Simple water molecule
    
    print(f"   Adding: {test_name}")
    print(f"   StilBAR: {test_stilbar}")
    print(f"   SMILES: {test_smiles}")
    
    success, result = generator.add_compound(test_name, test_stilbar, test_smiles)
    
    if success:
        print(f"✅ Compound added successfully!")
        print(f"   Hash ID: {result}")
        
        # Verify it was added
        verification = generator.compound_manager.get_compound_by_stilbar(test_stilbar)
        if verification:
            print("✅ Verification: Compound found in database")
            
            # Clean up - delete the test compound
            print("🧹 Cleaning up test compound...")
            delete_result = generator.delete_compounds([result])
            if delete_result['success']:
                print("✅ Test compound deleted successfully")
            else:
                print("⚠️ Failed to delete test compound - you may need to delete manually")
                print(f"   Hash ID to delete: {result}")
            
            return True
        else:
            print("❌ Verification failed: Compound not found after adding")
            return False
    else:
        print(f"❌ Failed to add compound: {result}")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing Supabase StilBAR Application")
    print("=" * 50)
    
    tests = [
        ("Connection Test", test_connection),
        ("Database Read Test", test_database_read),
        ("Compound Lookup Test", test_compound_lookup),
        ("Add Compound Test", test_add_compound)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with error: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {status}: {test_name}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n🎉 All tests passed! Your Supabase setup is working correctly.")
    else:
        print("\n⚠️ Some tests failed. Check your Supabase configuration.")

if __name__ == "__main__":
    main()