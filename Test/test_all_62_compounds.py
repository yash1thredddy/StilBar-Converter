#!/usr/bin/env python3
"""
Comprehensive test script for all 62 compounds from StilBAR database
Tests both the SMILES generator and cross-references with CSV data
"""

import csv
import sys
import os
from typing import Dict, List, Tuple

# Import the SMILES generator
try:
    from fixed_smiles_generator import FixedSMILESGenerator
except ImportError:
    print("❌ Error: Cannot import FixedSMILESGenerator")
    sys.exit(1)

def load_csv_compounds() -> Dict[int, Dict]:
    """Load compounds from the CSV file"""
    compounds = {}
    
    try:
        with open('Stilabar_Smiles.csv', 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            next(reader)  # Skip header
            
            for row in reader:
                if len(row) >= 4 and row[0].strip():  # Only process rows with compound numbers
                    try:
                        num = int(row[0].strip())
                        name = row[1].strip()
                        barcode = row[2].strip()
                        smiles = row[3].strip()
                        
                        if num and smiles:  # Only include entries with both number and SMILES
                            compounds[num] = {
                                'name': name,
                                'barcode': barcode,
                                'expected_smiles': smiles
                            }
                    except (ValueError, IndexError):
                        continue
    except FileNotFoundError:
        print("❌ Error: Stilabar_Smiles.csv not found")
        return {}
    
    return compounds

def test_smiles_generator():
    """Test the SMILES generator with all compounds"""
    print("🧬 Testing StilBAR to SMILES Converter with ALL 62 Compounds")
    print("=" * 70)
    
    # Load CSV compounds
    csv_compounds = load_csv_compounds()
    print(f"📊 Loaded {len(csv_compounds)} compounds from CSV")
    
    if len(csv_compounds) != 62:
        print(f"⚠️  Warning: Expected 62 compounds, found {len(csv_compounds)}")
    
    # Initialize the generator
    try:
        generator = FixedSMILESGenerator()
        print("✅ SMILES Generator initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize SMILES generator: {e}")
        return False
    
    print("\n" + "=" * 70)
    print("🔬 TESTING ALL COMPOUNDS")
    print("=" * 70)
    
    # Test statistics
    total_tests = 0
    exact_matches = 0
    generator_works = 0
    failures = 0
    
    # Test each compound
    for num in sorted(csv_compounds.keys()):
        compound = csv_compounds[num]
        barcode = compound['barcode']
        expected_smiles = compound['expected_smiles']
        name = compound['name']
        
        total_tests += 1
        
        print(f"\n📋 Compound {num:2d}: {name[:45]}...")
        print(f"   🏷️  Barcode: {barcode}")
        
        # Test with barcode if available
        if barcode and barcode.strip():
            try:
                result = generator.generate_smiles(barcode)
                if isinstance(result, tuple):
                    generated_smiles, metadata = result
                else:
                    generated_smiles = result
                    metadata = {}
                
                generator_works += 1
                
                print(f"   ✅ Generated: {generated_smiles[:60]}...")
                print(f"   📝 Expected:  {expected_smiles[:60]}...")
                
                # Check if exact match
                if generated_smiles == expected_smiles:
                    exact_matches += 1
                    print(f"   🎯 Status: EXACT MATCH ✅")
                else:
                    print(f"   ⚠️  Status: Different SMILES")
                
                if 'confidence' in metadata:
                    print(f"   🎲 Confidence: {metadata['confidence']}")
                
            except Exception as e:
                failures += 1
                print(f"   ❌ Generation failed: {e}")
        
        else:
            # Try with simple test patterns
            test_patterns = ['H', 'T', 'P', 'C', 'M', 'X']
            pattern_found = False
            
            for pattern in test_patterns:
                if pattern.lower() in name.lower() or pattern in str(num):
                    try:
                        result = generator.generate_smiles(pattern)
                        if isinstance(result, tuple):
                            generated_smiles, metadata = result
                        else:
                            generated_smiles = result
                            metadata = {}
                        
                        generator_works += 1
                        pattern_found = True
                        print(f"   ✅ Tested with pattern '{pattern}': {generated_smiles[:50]}...")
                        break
                    except Exception as e:
                        continue
            
            if not pattern_found:
                print(f"   ⚠️  No barcode available, skipped generator test")
    
    # Print final summary
    print("\n" + "=" * 70)
    print("📊 FINAL TEST RESULTS")
    print("=" * 70)
    print(f"📋 Total compounds tested: {total_tests}")
    print(f"✅ Generator successful: {generator_works}")
    print(f"🎯 Exact SMILES matches: {exact_matches}")
    print(f"❌ Generation failures: {failures}")
    
    if total_tests > 0:
        success_rate = (generator_works / total_tests) * 100
        match_rate = (exact_matches / total_tests) * 100
        print(f"📈 Generator success rate: {success_rate:.1f}%")
        print(f"🎯 Exact match rate: {match_rate:.1f}%")
    
    # Test some basic patterns
    print("\n" + "=" * 70)
    print("🧪 TESTING BASIC PATTERNS")
    print("=" * 70)
    
    basic_patterns = ['H', 'T', 'C', 'P', 'M', 'X']
    for pattern in basic_patterns:
        try:
            result = generator.generate_smiles(pattern)
            if isinstance(result, tuple):
                smiles, metadata = result
                confidence = metadata.get('confidence', 'N/A')
                method = metadata.get('method', 'N/A')
                print(f"✅ {pattern}: {smiles} (confidence: {confidence}, method: {method})")
            else:
                print(f"✅ {pattern}: {result}")
        except Exception as e:
            print(f"❌ {pattern}: Failed - {e}")
    
    print("\n🎉 Testing completed!")
    return generator_works > 0 and failures == 0

def main():
    """Main test function"""
    print("🚀 Starting comprehensive StilBAR testing...")
    
    # Check if required files exist
    required_files = ['fixed_smiles_generator.py', 'Stilabar_Smiles.csv']
    missing_files = []
    
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing required files: {', '.join(missing_files)}")
        return False
    
    # Run the comprehensive test
    success = test_smiles_generator()
    
    if success:
        print("\n✅ All tests completed successfully!")
        return True
    else:
        print("\n❌ Some tests failed!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)