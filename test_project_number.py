#!/usr/bin/env python
"""Test Firestore with project number vs project ID"""
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
print("Testing Firestore Project Configuration")
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
    
    original_project_id = service_account_dict.get('project_id')
    project_number = service_account_dict.get('project_number')
    
    print(f"Service Account Info:")
    print(f"  project_id: {original_project_id}")
    print(f"  project_number: {project_number}")
    print(f"  client_email: {service_account_dict.get('client_email')}")
    print(f"\nUser provided: 458510671023 (might be project number)\n")
    
    # Import Google Cloud Firestore
    from google.cloud import firestore
    from google.oauth2 import service_account
    
    credentials_obj = service_account.Credentials.from_service_account_info(
        service_account_dict
    )
    
    # Test 1: Original project ID
    print("="*60)
    print("Test 1: Using original project_id from credentials")
    print("="*60)
    try:
        db1 = firestore.Client(project=original_project_id, credentials=credentials_obj)
        print(f"✓ Connected with project_id: {original_project_id}")
        
        # Try to list collections
        try:
            collections = list(db1.collections())
            print(f"  Collections found: {len(collections)}")
            for col in collections[:5]:
                print(f"    - {col.id}")
        except:
            print("  Could not list collections")
        
        # Test products
        products_ref = db1.collection("products")
        docs = list(products_ref.limit(5).stream())
        print(f"  Products collection: {len(docs)} documents")
        
    except Exception as e:
        print(f"  ✗ Error: {e}")
    
    # Test 2: Using project number as project ID
    print("\n" + "="*60)
    print("Test 2: Using project number as project ID")
    print("="*60)
    try:
        db2 = firestore.Client(project="458510671023", credentials=credentials_obj)
        print("✓ Connected with project: 458510671023")
        
        products_ref = db2.collection("products")
        docs = list(products_ref.limit(5).stream())
        print(f"  Products collection: {len(docs)} documents")
        
    except Exception as e:
        print(f"  ✗ Error: {e}")
    
    # Test 3: Check if we need to specify database
    print("\n" + "="*60)
    print("Test 3: Checking for multiple databases")
    print("="*60)
    print("Note: Firestore supports multiple databases per project.")
    print("If your data is in a non-default database, we need to specify it.")
    print("\nTo check available databases:")
    print("  1. Go to Firebase Console")
    print("  2. Check Firestore Database section")
    print("  3. Look for database names (usually 'default' or custom names)")
    
    # Test 4: Try with database parameter (if supported)
    print("\n" + "="*60)
    print("Test 4: Testing with explicit database parameter")
    print("="*60)
    try:
        # Try to create client with database parameter
        # Note: This might require a different initialization
        db3 = firestore.Client(project=original_project_id, credentials=credentials_obj)
        print(f"✓ Using project: {original_project_id}")
        print("  (Database parameter not directly supported in this version)")
        print("  If you have multiple databases, you may need to:")
        print("  1. Use the correct project ID")
        print("  2. Ensure the service account has access to the correct project")
        print("  3. Check if data is in a different region")
        
    except Exception as e:
        print(f"  ✗ Error: {e}")
    
    print("\n" + "="*60)
    print("Recommendations")
    print("="*60)
    print("\n1. Verify the project ID in Firebase Console:")
    print(f"   - Current credentials point to: {original_project_id}")
    print(f"   - You mentioned: 458510671023 (this is likely a project number)")
    print("\n2. Check if the service account has access to the correct project")
    print("\n3. Verify the database exists and is in the correct region")
    print("\n4. If 458510671023 is the correct project, you may need:")
    print("   - A service account for that project")
    print("   - Or update the project_id in the service account JSON")
    
except KeyboardInterrupt:
    print("\n\n⚠ Interrupted by user")
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

