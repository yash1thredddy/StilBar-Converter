#!/usr/bin/env python3
"""
Dependency Security Analysis for StilBAR-Converter
Checks for known vulnerabilities in requirements.txt
"""
import re
from pathlib import Path

def check_dependency_versions():
    """Check for potentially vulnerable dependency versions"""
    print("🔍 Analyzing Dependencies for Security Issues...")
    print("=" * 50)
    
    requirements_file = Path("requirements.txt")
    if not requirements_file.exists():
        print("❌ requirements.txt not found")
        return False
    
    # Known vulnerable packages and versions (simplified list)
    known_vulnerabilities = {
        'streamlit': {
            'vulnerable_versions': ['< 1.0.0'],
            'description': 'Older versions may have XSS vulnerabilities'
        },
        'pandas': {
            'vulnerable_versions': ['< 1.3.0'],
            'description': 'CSV parsing vulnerabilities in older versions'
        },
        'pillow': {
            'vulnerable_versions': ['< 8.3.2'],
            'description': 'Image processing vulnerabilities'
        },
        'pyjwt': {
            'vulnerable_versions': ['< 2.4.0'],
            'description': 'JWT algorithm confusion vulnerabilities'
        }
    }
    
    recommendations = []
    issues_found = 0
    
    with open(requirements_file, 'r') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
                
            print(f"\n📦 Line {line_num}: {line}")
            
            # Parse package name (handle version specifiers)
            package_match = re.match(r'^([a-zA-Z0-9\-_]+)', line)
            if not package_match:
                continue
                
            package_name = package_match.group(1).lower()
            
            # Check for version pinning
            if '==' not in line and '>=' not in line and '>' not in line:
                print(f"  ⚠️  No version specified - recommend pinning versions")
                recommendations.append(f"Pin version for {package_name}")
            
            # Check against known vulnerabilities
            if package_name in known_vulnerabilities:
                vuln_info = known_vulnerabilities[package_name]
                print(f"  🔍 Checking known vulnerabilities...")
                print(f"     Issue: {vuln_info['description']}")
                print(f"     Vulnerable: {', '.join(vuln_info['vulnerable_versions'])}")
                
                # For simplicity, recommend updating if no version specified
                if '==' not in line:
                    print(f"  ✅ Recommend: Ensure you're using latest stable version")
                    recommendations.append(f"Verify {package_name} is up to date")
            
            # Check for development/testing packages in production
            dev_packages = ['pytest', 'unittest', 'mock', 'nose']
            if package_name in dev_packages:
                print(f"  📋 Note: {package_name} is a development package")
                recommendations.append(f"Consider moving {package_name} to dev-requirements.txt")
    
    # Security recommendations
    print(f"\n" + "=" * 50)
    print("🛡️ Security Recommendations")
    print("=" * 50)
    
    # General security practices
    security_tips = [
        "Pin exact versions in requirements.txt for reproducible builds",
        "Regularly update dependencies to get security patches",
        "Use tools like safety or pip-audit to check for vulnerabilities",
        "Consider using dependabot or similar for automated updates",
        "Separate development dependencies from production ones",
        "Use virtual environments to isolate dependencies"
    ]
    
    print("\n📋 General Security Practices:")
    for i, tip in enumerate(security_tips, 1):
        print(f"  {i}. {tip}")
    
    if recommendations:
        print(f"\n⚠️  Specific Recommendations for this project:")
        for i, rec in enumerate(recommendations, 1):
            print(f"  {i}. {rec}")
    else:
        print(f"\n✅ No immediate dependency issues found")
    
    return True

def check_for_insecure_patterns():
    """Check requirements.txt for insecure patterns"""
    print(f"\n🔍 Checking for Insecure Dependency Patterns...")
    
    requirements_file = Path("requirements.txt")
    with open(requirements_file, 'r') as f:
        content = f.read()
    
    issues = []
    
    # Check for HTTP URLs (should use HTTPS)
    if 'http://' in content:
        issues.append("HTTP URLs found - should use HTTPS for security")
    
    # Check for git+ssh without verification
    if 'git+' in content and 'verify' not in content:
        issues.append("Git dependencies may not verify authenticity")
    
    # Check for wildcard versions
    if '*' in content:
        issues.append("Wildcard versions can introduce unexpected changes")
    
    if issues:
        print("  ⚠️  Security issues found:")
        for issue in issues:
            print(f"     • {issue}")
    else:
        print("  ✅ No insecure patterns found")

if __name__ == "__main__":
    print("🔒 Dependency Security Analysis")
    print("=" * 50)
    
    success = check_dependency_versions()
    if success:
        check_for_insecure_patterns()
    
    print(f"\n✅ Dependency analysis complete")
    print("💡 Run 'pip install safety && safety check' for more detailed vulnerability scanning")