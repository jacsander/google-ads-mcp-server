#!/usr/bin/env python
"""
Setup verification script for Google Ads MCP Server.
Checks prerequisites and configuration.
"""

import sys
import os
import subprocess
from pathlib import Path


def check_python_version():
    """Check if Python version is 3.10 or higher."""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 10:
        print(f"✓ Python {version.major}.{version.minor}.{version.micro} (required: 3.10+)")
        return True
    else:
        print(f"✗ Python {version.major}.{version.minor}.{version.micro} (required: 3.10+)")
        return False


def check_package_installed(package_name):
    """Check if a Python package is installed."""
    try:
        __import__(package_name.replace("-", "_"))
        print(f"✓ {package_name} is installed")
        return True
    except ImportError:
        print(f"✗ {package_name} is not installed")
        return False


def check_environment_variable(var_name, required=True):
    """Check if an environment variable is set."""
    value = os.environ.get(var_name)
    if value:
        # Mask sensitive values
        if "TOKEN" in var_name or "CREDENTIALS" in var_name:
            display_value = value[:10] + "..." if len(value) > 10 else "***"
        else:
            display_value = value
        print(f"✓ {var_name} is set: {display_value}")
        return True
    else:
        if required:
            print(f"✗ {var_name} is not set (REQUIRED)")
        else:
            print(f"○ {var_name} is not set (optional)")
        return not required


def check_credentials_file():
    """Check if credentials file exists."""
    creds_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if not creds_path:
        print("○ GOOGLE_APPLICATION_CREDENTIALS not set, cannot check file")
        return False
    
    path = Path(creds_path)
    if path.exists():
        print(f"✓ Credentials file exists: {creds_path}")
        return True
    else:
        print(f"✗ Credentials file not found: {creds_path}")
        return False


def check_gcloud_installed():
    """Check if gcloud CLI is installed."""
    try:
        result = subprocess.run(
            ["gcloud", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            version_line = result.stdout.split("\n")[0]
            print(f"✓ gcloud is installed: {version_line}")
            return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    
    print("○ gcloud CLI is not installed (optional, but recommended for authentication)")
    return False


def check_pipx_installed():
    """Check if pipx is installed."""
    try:
        result = subprocess.run(
            ["pipx", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"✓ pipx is installed: {version}")
            return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    
    print("○ pipx is not installed (optional, but recommended for MCP servers)")
    return False


def main():
    """Run all checks."""
    print("=" * 60)
    print("Google Ads MCP Server - Setup Verification")
    print("=" * 60)
    print()
    
    checks = []
    
    print("Prerequisites:")
    print("-" * 60)
    checks.append(("Python version", check_python_version()))
    checks.append(("pipx", check_pipx_installed()))
    checks.append(("gcloud CLI", check_gcloud_installed()))
    print()
    
    print("Python Packages:")
    print("-" * 60)
    checks.append(("google-ads", check_package_installed("google.ads.googleads")))
    checks.append(("mcp", check_package_installed("mcp")))
    print()
    
    print("Environment Variables:")
    print("-" * 60)
    checks.append(("GOOGLE_ADS_DEVELOPER_TOKEN", check_environment_variable("GOOGLE_ADS_DEVELOPER_TOKEN", required=True)))
    checks.append(("GOOGLE_APPLICATION_CREDENTIALS", check_environment_variable("GOOGLE_APPLICATION_CREDENTIALS", required=True)))
    checks.append(("GOOGLE_PROJECT_ID", check_environment_variable("GOOGLE_PROJECT_ID", required=False)))
    checks.append(("GOOGLE_ADS_LOGIN_CUSTOMER_ID", check_environment_variable("GOOGLE_ADS_LOGIN_CUSTOMER_ID", required=False)))
    print()
    
    print("Credentials:")
    print("-" * 60)
    checks.append(("Credentials file", check_credentials_file()))
    print()
    
    print("=" * 60)
    required_checks = [name for name, result in checks if "TOKEN" in name or "CREDENTIALS" in name or name == "Python version" or name == "google-ads"]
    passed_required = all(result for name, result in checks if name in required_checks)
    
    if passed_required:
        print("✓ All required checks passed!")
        print()
        print("Next steps:")
        print("1. Configure your MCP client (Cursor, Claude Desktop, etc.)")
        print("2. See SETUP_LOCAL.md for detailed configuration instructions")
    else:
        print("✗ Some required checks failed. Please fix the issues above.")
        print()
        print("See SETUP_LOCAL.md for setup instructions.")
    
    print("=" * 60)
    
    return 0 if passed_required else 1


if __name__ == "__main__":
    sys.exit(main())

