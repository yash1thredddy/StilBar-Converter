#!/usr/bin/env python3
"""
Security Test Suite for StilBAR-Converter
Tests security fixes and validates input validation
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from security_utils import (
    validate_stilbar_code, validate_smiles_input, validate_compound_name,
    validate_csv_file_size, sanitize_error_message
)

def test_input_validation():
    """Test input validation functions"""
    print("🧪 Testing Input Validation...")
    
    # Test StilBAR code validation
    print("\n📝 StilBAR Code Validation:")
    
    # Valid cases
    valid_stilbar = ["H-77-H", "T|–04r.15r–|H", "H", "simple123"]
    for code in valid_stilbar:
        valid, error = validate_stilbar_code(code)
        print(f"  ✅ '{code}': {valid} (Expected: True)")
        assert valid, f"Should be valid: {code}"
    
    # Invalid cases
    invalid_stilbar = ["", "a" * 501, "invalid<script>", "test\x00null"]
    for code in invalid_stilbar:
        valid, error = validate_stilbar_code(code)
        print(f"  ❌ '{code[:20]}...': {valid} - {error}")
        assert not valid, f"Should be invalid: {code}"
    
    # Test SMILES validation
    print("\n🧬 SMILES Validation:")
    
    # Valid cases
    valid_smiles = ["OC1=CC=C(CCC2=CC=C(O)C=C2)C=C1", "C", "CCO"]
    for smiles in valid_smiles:
        valid, error = validate_smiles_input(smiles)
        print(f"  ✅ '{smiles[:30]}...': {valid} (Expected: True)")
        assert valid, f"Should be valid: {smiles}"
    
    # Invalid cases
    invalid_smiles = ["", "a" * 10001, "invalid<script>alert(1)</script>"]
    for smiles in invalid_smiles:
        valid, error = validate_smiles_input(smiles)
        print(f"  ❌ '{smiles[:20]}...': {valid} - {error}")
        assert not valid, f"Should be invalid: {smiles}"
    
    # Test compound name validation
    print("\n🏷️ Compound Name Validation:")
    
    # Valid cases
    valid_names = ["Compound_1", "Test-Compound", "Simple compound (123)"]
    for name in valid_names:
        valid, error = validate_compound_name(name)
        print(f"  ✅ '{name}': {valid} (Expected: True)")
        assert valid, f"Should be valid: {name}"
    
    # Invalid cases
    invalid_names = ["", "a" * 201, "invalid<script>", "test\x00null"]
    for name in invalid_names:
        valid, error = validate_compound_name(name)
        print(f"  ❌ '{name[:20]}...': {valid} - {error}")
        assert not valid, f"Should be invalid: {name}"

def test_file_validation():
    """Test file size validation"""
    print("\n📁 File Size Validation:")
    
    # Valid file sizes
    valid_sizes = [1000, 5 * 1024 * 1024]  # 1KB, 5MB
    for size in valid_sizes:
        valid, error = validate_csv_file_size(size)
        print(f"  ✅ {size} bytes: {valid} (Expected: True)")
        assert valid, f"Should be valid size: {size}"
    
    # Invalid file sizes
    invalid_sizes = [15 * 1024 * 1024, 100 * 1024 * 1024]  # 15MB, 100MB
    for size in invalid_sizes:
        valid, error = validate_csv_file_size(size)
        print(f"  ❌ {size} bytes: {valid} - {error}")
        assert not valid, f"Should be invalid size: {size}"

def test_error_sanitization():
    """Test error message sanitization"""
    print("\n🛡️ Error Message Sanitization:")
    
    # Test different types of errors
    test_errors = [
        Exception("Database connection failed: postgresql://user:pass@host/db"),
        Exception("FileNotFoundError: /secret/path/file.txt not found"),
        Exception("Authentication failed: Invalid API key abc123def456"),
        Exception("Simple error message")
    ]
    
    for error in test_errors:
        sanitized = sanitize_error_message(error)
        print(f"  Original: {str(error)}")
        print(f"  Sanitized: {sanitized}")
        
        # Check that sensitive info is not exposed
        error_str = str(error).lower()
        sanitized_lower = sanitized.lower()
        
        # Should not contain passwords, keys, or paths
        sensitive_terms = ['password', 'pass@', 'key', '/secret/', 'abc123']
        for term in sensitive_terms:
            if term in error_str:
                assert term not in sanitized_lower, f"Sensitive term '{term}' found in sanitized message"
        
        print(f"  ✅ Sanitization successful\n")

def run_security_tests():
    """Run all security tests"""
    print("🔒 Running Security Test Suite")
    print("=" * 50)
    
    try:
        test_input_validation()
        test_file_validation()
        test_error_sanitization()
        
        print("\n" + "=" * 50)
        print("✅ All Security Tests Passed!")
        print("🛡️ Security fixes are working correctly")
        return True
        
    except AssertionError as e:
        print(f"\n❌ Security Test Failed: {e}")
        return False
    except Exception as e:
        print(f"\n💥 Test Error: {e}")
        return False

if __name__ == "__main__":
    success = run_security_tests()
    sys.exit(0 if success else 1)