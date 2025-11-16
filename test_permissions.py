#!/usr/bin/env python
"""Test Firestore permissions and try to read/write"""
import os
import sys
import json
import base64
from datetime import datetime

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
print("Testing Firestore Permissions")
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
    client_email = service_account_dict.get('client_email')
    
    print(f"Project ID: {project_id}")
    print(f"Service Account: {client_email}\n")
    
    # Import Google Cloud Firestore
    from google.cloud import firestore
    from google.oauth2 import service_account
    
    credentials_obj = service_account.Credentials.from_service_account_info(
        service_account_dict
    )
    db = firestore.Client(project=project_id, credentials=credentials_obj)
    print("✓ Connected to Firestore\n")
    
    # Test 1: Try to read from products
    print("="*60)
    print("Test 1: Reading from 'products' collection")
    print("="*60)
    try:
        products_ref = db.collection("products")
        
        # Try different query methods
        print("\n1.1. Using stream() without limit:")
        docs = list(products_ref.stream())
        print(f"   Result: {len(docs)} documents")
        
        print("\n1.2. Using stream() with limit(100):")
        docs = list(products_ref.limit(100).stream())
        print(f"   Result: {len(docs)} documents")
        
        print("\n1.3. Using get() on a specific document (if any exist):")
        # Try to get a document by ID (common IDs to try)
        test_ids = ["test", "1", "product1", "sample"]
        for test_id in test_ids:
            try:
                doc_ref = products_ref.document(test_id)
                doc = doc_ref.get()
                if doc.exists:
                    print(f"   ✓ Found document '{test_id}': {doc.to_dict()}")
                    break
            except:
                pass
        else:
            print("   No documents found with test IDs")
        
        print("\n1.4. Checking if collection reference is accessible:")
        print(f"   Collection path: {products_ref.path}")
        print(f"   ✓ Collection reference is valid")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 2: Try to write a test document (to check write permissions)
    print("\n" + "="*60)
    print("Test 2: Testing write permissions (will delete after)")
    print("="*60)
    try:
        test_collection = db.collection("_test_permissions")
        test_doc_ref = test_collection.document("test_read_write")
        
        # Try to write
        test_data = {
            "test": True,
            "timestamp": datetime.now(),
            "message": "Permission test"
        }
        test_doc_ref.set(test_data)
        print("   ✓ Write successful!")
        
        # Try to read it back
        doc = test_doc_ref.get()
        if doc.exists:
            print(f"   ✓ Read back successful: {doc.to_dict()}")
        
        # Delete the test document
        test_doc_ref.delete()
        print("   ✓ Test document deleted")
        
    except Exception as e:
        print(f"   ⚠ Write test failed: {e}")
        print("   This might indicate write permissions are restricted")
    
    # Test 3: Check service account roles/permissions
    print("\n" + "="*60)
    print("Test 3: Service Account Information")
    print("="*60)
    print(f"   Service Account Email: {client_email}")
    print(f"   Project ID: {project_id}")
    print("\n   Note: To check IAM roles, you need to:")
    print("   1. Go to Google Cloud Console")
    print("   2. Navigate to IAM & Admin > IAM")
    print("   3. Find the service account: {client_email}")
    print("   4. Check if it has 'Cloud Datastore User' or 'Firestore User' role")
    
    # Test 4: Try different database/region
    print("\n" + "="*60)
    print("Test 4: Checking database configuration")
    print("="*60)
    print(f"   Database client: {type(db).__name__}")
    print(f"   Project: {db.project}")
    
    # Summary
    print("\n" + "="*60)
    print("Summary & Recommendations")
    print("="*60)
    print("\nIf collections show 0 documents but you know they have data:")
    print("  1. Check Firestore Security Rules in Firebase Console")
    print("  2. Verify service account has 'Cloud Datastore User' role")
    print("  3. Check if data is in a different Firestore database")
    print("  4. Verify you're connecting to the correct project")
    print("  5. Check if collections are in a different region")
    
    print("\n" + "="*60)
    print("✅ Permission test completed!")
    print("="*60)

except KeyboardInterrupt:
    print("\n\n⚠ Interrupted by user")
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

