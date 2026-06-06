"""
Production Readiness Audit - Full System Check
"""
import os
import sys
import json
from pathlib import Path

BASE_DIR = Path(".")
ISSUES = []
WARNINGS = []
PASSES = []

def check_env_variables():
    """Check .env file and required environment variables"""
    print("\n=== ENVIRONMENT VARIABLES ===")
    
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    # Check if .env exists
    if not env_file.exists():
        ISSUES.append("Missing .env file - required for API keys and configuration")
    else:
        PASSES.append(".env file exists")
        
        # Check required keys
        with open(env_file, encoding='utf-8', errors='ignore') as f:
            env_content = f.read()
            required_keys = ["OPENAI_API_KEY", "GROQ_API_KEY", "SECRET_KEY", "DATABASE_URL"]
            for key in required_keys:
                if key in env_content:
                    PASSES.append(f"  ✓ {key} present")
                else:
                    WARNINGS.append(f"  ⚠ {key} not found in .env")
    
    # Check for hardcoded secrets in code
    print("\nChecking for hardcoded secrets in Python files...")
    for py_file in BASE_DIR.rglob("*.py"):
        if "venv" in str(py_file) or "__pycache__" in str(py_file):
            continue
        with open(py_file) as f:
            content = f.read()
            if "your-super-secret-key" in content:
                ISSUES.append(f"Hardcoded default SECRET_KEY in {py_file.relative_to(BASE_DIR)}")
            if "sk-" in content and len(content.split("sk-")[1].split()[0]) > 30:
                ISSUES.append(f"Potential hardcoded API key in {py_file.relative_to(BASE_DIR)}")

def check_hardcoded_ips():
    """Check for hardcoded localhost/IP addresses"""
    print("\n=== HARDCODED IPs / LOCALHOST REFERENCES ===")
    
    hardcoded_patterns = {
        "localhost": [],
        "127.0.0.1": [],
        "192.168": [],
        "0.0.0.0": [],
        "LAN": []
    }
    
    for py_file in BASE_DIR.rglob("*.py"):
        if "venv" in str(py_file) or "__pycache__" in str(py_file) or "audit_test" in str(py_file):
            continue
        with open(py_file) as f:
            for line_num, line in enumerate(f, 1):
                for pattern in hardcoded_patterns:
                    if pattern.lower() in line.lower():
                        hardcoded_patterns[pattern].append(f"{py_file.relative_to(BASE_DIR)}:{line_num}")
    
    for pattern, files in hardcoded_patterns.items():
        if files:
            print(f"\n{pattern}: {len(files)} occurrences")
            for f in files[:3]:  # Show first 3
                print(f"  - {f}")
                
    # Check JavaScript files
    for js_file in BASE_DIR.rglob("*.js"):
        if "node_modules" in str(js_file):
            continue
        with open(js_file) as f:
            content = f.read()
            if "http://localhost" in content or "http://127" in content:
                WARNINGS.append(f"Hardcoded localhost in {js_file.relative_to(BASE_DIR)}")
                if "http://192.168.0.39:8000" in content:
                    WARNINGS.append(f"  → Mobile app has hardcoded backend URL - needs env config for production")

def check_pydantic_orm_mode():
    """Check for deprecated Pydantic orm_mode"""
    print("\n=== PYDANTIC V2 COMPATIBILITY ===")
    
    orm_mode_issues = []
    for py_file in BASE_DIR.rglob("*.py"):
        if "venv" in str(py_file) or "__pycache__" in str(py_file):
            continue
        with open(py_file) as f:
            content = f.read()
            if "orm_mode" in content:
                orm_mode_issues.append(py_file.relative_to(BASE_DIR))
    
    if orm_mode_issues:
        WARNINGS.append(f"Deprecated 'orm_mode' found in Pydantic models ({len(orm_mode_issues)} files)")
        WARNINGS.append(f"  → Use 'from_attributes = True' instead of 'orm_mode = True'")
        for f in orm_mode_issues[:3]:
            print(f"    {f}")
    else:
        PASSES.append("No deprecated Pydantic orm_mode usage")

def check_database():
    """Check database configuration"""
    print("\n=== DATABASE CONFIGURATION ===")
    
    # Check for SQLite in production
    with open("database.py") as f:
        db_content = f.read()
        if "sqlite" in db_content.lower():
            WARNINGS.append("SQLite database used - not suitable for production")
            WARNINGS.append("  → For production, use PostgreSQL or MySQL")
    
    # Check migrations
    if not Path("migrations").exists():
        WARNINGS.append("No database migrations found - manual schema management required")
    else:
        PASSES.append("Database migrations directory exists")

def check_mobile_app():
    """Check React Native mobile app configuration"""
    print("\n=== MOBILE APP CONFIGURATION ===")
    
    # Check package.json
    package_file = Path("mobile_app/package.json")
    if package_file.exists():
        with open(package_file) as f:
            package_data = json.load(f)
            PASSES.append(f"Mobile app configured: {package_data.get('name', 'N/A')}")
            
            deps = package_data.get("dependencies", {})
            required = ["react-native", "expo", "@react-navigation/native"]
            for dep in required:
                if dep in deps:
                    PASSES.append(f"  ✓ {dep}: {deps[dep]}")
    
    # Check API configuration
    api_js = Path("mobile_app/services/api.js")
    if api_js.exists():
        with open(api_js) as f:
            api_content = f.read()
            if "getApiBase()" in api_content:
                PASSES.append("API base URL is dynamically configured")
            else:
                ISSUES.append("API base URL might be hardcoded in mobile app")

def check_cors():
    """Check CORS configuration"""
    print("\n=== CORS CONFIGURATION ===")
    
    with open("main.py") as f:
        main_content = f.read()
        if 'allow_origins=["*"]' in main_content:
            WARNINGS.append("CORS allow_origins=['*'] - allows any domain (fine for local dev)")
            WARNINGS.append("  → For production, restrict to specific domains")
        else:
            PASSES.append("CORS configuration found")

def check_error_handling():
    """Check error handling"""
    print("\n=== ERROR HANDLING ===")
    
    errors_without_details = []
    for py_file in BASE_DIR.rglob("*.py"):
        if "venv" in str(py_file) or "__pycache__" in str(py_file) or "audit" in str(py_file):
            continue
        with open(py_file) as f:
            lines = f.readlines()
            for i, line in enumerate(lines):
                if "except Exception" in line and "str(e)" in lines[i+1]:
                    errors_without_details.append(str(py_file.relative_to(BASE_DIR)))
                    break
    
    if errors_without_details:
        WARNINGS.append(f"Generic Exception handling found in {len(errors_without_details)} files")
        WARNINGS.append("  → Add specific exception types and logging for production debugging")
    else:
        PASSES.append("Specific exception handling patterns observed")

def check_logging():
    """Check logging configuration"""
    print("\n=== LOGGING CONFIGURATION ===")
    
    if Path("services/logging_config.py").exists():
        PASSES.append("Logging configuration file exists")
    else:
        WARNINGS.append("No centralized logging configuration found")

def check_jwt_security():
    """Check JWT security"""
    print("\n=== JWT SECURITY ===")
    
    with open("auth.py") as f:
        auth_content = f.read()
        
        if 'SECRET_KEY = os.getenv("SECRET_KEY"' in auth_content:
            PASSES.append("SECRET_KEY loaded from environment variables")
        else:
            ISSUES.append("SECRET_KEY not properly loaded from environment")
        
        if "ALGORITHM" in auth_content:
            PASSES.append("JWT algorithm configuration found")

def check_docker():
    """Check Docker configuration"""
    print("\n=== DOCKER CONFIGURATION ===")
    
    if Path("Dockerfile").exists():
        PASSES.append("Dockerfile exists")
        with open("Dockerfile") as f:
            dockerfile_content = f.read()
            if "python:3.11-slim" in dockerfile_content:
                PASSES.append("  ✓ Using slim Python image (good for production)")
            if "EXPOSE 8000" in dockerfile_content:
                PASSES.append("  ✓ Port 8000 exposed")
    else:
        WARNINGS.append("No Dockerfile found")
    
    if Path("docker-compose.yml").exists():
        PASSES.append("docker-compose.yml exists")
    else:
        WARNINGS.append("No docker-compose.yml found for easy local testing")

# Run all checks
print("=" * 70)
print("PRODUCTION READINESS AUDIT - AI MONEY MENTOR")
print("=" * 70)

check_env_variables()
check_hardcoded_ips()
check_pydantic_orm_mode()
check_database()
check_mobile_app()
check_cors()
check_error_handling()
check_logging()
check_jwt_security()
check_docker()

# Summary
print("\n" + "=" * 70)
print("AUDIT SUMMARY")
print("=" * 70)
print(f"\n✓ PASSES:   {len(PASSES)}")
print(f"⚠ WARNINGS: {len(WARNINGS)}")
print(f"✗ ISSUES:   {len(ISSUES)}")

if ISSUES:
    print("\n🔴 CRITICAL ISSUES (Blocking Deployment):")
    for issue in ISSUES:
        print(f"  ✗ {issue}")

if WARNINGS:
    print("\n🟡 WARNINGS (Should Fix Before Production):")
    for warning in WARNINGS:
        print(f"  ⚠ {warning}")

print("\n✓ PASSING CHECKS:")
for passed in PASSES[:5]:  # Show first 5
    print(f"  ✓ {passed}")
if len(PASSES) > 5:
    print(f"  ... and {len(PASSES) - 5} more")

sys.exit(0 if len(ISSUES) == 0 else 1)
