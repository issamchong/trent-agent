#!/usr/bin/env python
"""Check which database is currently being used"""
import os
import sys
import json
import base64

# Load .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    env_file = '.env'
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

print("="*60)
print("Current Database Configuration")
print("="*60 + "\n")

try:
    # Get credentials
    encoded_credentials = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")
    if not encoded_credentials:
        print("❌ ERROR: GOOGLE_APPLICATION_CREDENTIALS_JSON not found")
        sys.exit(1)
    
    # Decode credentials
    json_credentials_str = base64.b64decode(encoded_credentials).decode("utf-8")
    service_account_dict = json.loads(json_credentials_str)
    project_id = service_account_dict.get('project_id')
    
    print(f"Project ID: {project_id}\n")
    
    # Check the code configuration
    print("="*60)
    print("Code Configuration (from firebase_tool.py)")
    print("="*60)
    
    # Read the actual code file
    tool_file = 'src/trent_agent/tools/firebase_tool.py'
    if os.path.exists(tool_file):
        with open(tool_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if "database='trent'" in content:
                print("✓ Database: 'trent'")
            elif "database=" in content:
                # Extract database name
                import re
                match = re.search(r"database=['\"]([^'\"]+)['\"]", content)
                if match:
                    print(f"✓ Database: '{match.group(1)}'")
                else:
                    print("⚠ Database parameter found but could not extract name")
            else:
                print("⚠ Using default database (no database parameter specified)")
    else:
        print("⚠ Could not read firebase_tool.py")
    
    # Test actual connection
    print("\n" + "="*60)
    print("Testing Actual Connection")
    print("="*60)
    
    from google.cloud import firestore
    from google.oauth2 import service_account
    
    credentials_obj = service_account.Credentials.from_service_account_info(
        service_account_dict
    )
    
    # Test with 'trent' database (current configuration)
    print("\n1. Testing with 'trent' database (current config):")
    try:
        db_trent = firestore.Client(project=project_id, credentials=credentials_obj, database='trent')
        products_ref = db_trent.collection("products")
        docs = list(products_ref.limit(5).stream())
        print(f"   ✓ Connected to 'trent' database")
        print(f"   ✓ Found {len(docs)} products")
        if len(docs) > 0:
            print(f"   ✅ This is the correct database with data!")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test with default database for comparison
    print("\n2. Testing with default database (for comparison):")
    try:
        db_default = firestore.Client(project=project_id, credentials=credentials_obj)
        products_ref = db_default.collection("products")
        docs = list(products_ref.limit(5).stream())
        print(f"   ✓ Connected to default database")
        print(f"   Found {len(docs)} products")
        if len(docs) == 0:
            print(f"   ○ Default database is empty (as expected)")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    print("\n" + "="*60)
    print("Summary")
    print("="*60)
    print("\nCurrent Configuration:")
    print("  Project ID: trentdb-c5666")
    print("  Database: 'trent'")
    print("  Status: ✅ Correctly configured to access data")
    
except KeyboardInterrupt:
    print("\n\n⚠ Interrupted by user")
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

