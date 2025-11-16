#!/usr/bin/env python
"""Test Google Cloud Firestore access directly"""
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
print("Testing Google Cloud Firestore Direct Access")
print("="*60 + "\n")

try:
    # Get credentials
    encoded_credentials = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")
    if not encoded_credentials:
        print("❌ ERROR: GOOGLE_APPLICATION_CREDENTIALS_JSON not found")
        sys.exit(1)
    
    print("✓ Credentials found")
    
    # Decode credentials
    json_credentials_str = base64.b64decode(encoded_credentials).decode("utf-8")
    service_account_dict = json.loads(json_credentials_str)
    project_id = service_account_dict.get('project_id')
    
    print(f"✓ Project ID: {project_id}")
    print(f"✓ Client Email: {service_account_dict.get('client_email', 'N/A')}\n")
    
    # Import Google Cloud Firestore (NOT Firebase Admin SDK)
    print("Importing google.cloud.firestore...")
    from google.cloud import firestore
    from google.oauth2 import service_account
    print("✓ Imported google.cloud.firestore\n")
    
    # Create credentials object
    print("Creating service account credentials...")
    credentials_obj = service_account.Credentials.from_service_account_info(
        service_account_dict
    )
    print("✓ Credentials object created\n")
    
    # Initialize Firestore client (Google Cloud side)
    print("Initializing Firestore client...")
    print("  Using: firestore.Client(project=project_id, credentials=credentials_obj)")
    db = firestore.Client(project=project_id, credentials=credentials_obj)
    print("✓ Firestore client initialized\n")
    
    # Test 1: List collections (if permissions allow)
    print("="*60)
    print("Test 1: Checking collections access")
    print("="*60)
    try:
        # Note: list_collections() might require additional permissions
        collections = list(db.collections())
        print(f"✓ Found {len(collections)} collections:")
        for col in collections:
            print(f"  - {col.id}")
    except Exception as e:
        print(f"⚠ Could not list collections (might need permissions): {e}")
        print("  This is okay - we'll test direct collection access\n")
    
    # Test 2: Access products collection
    print("\n" + "="*60)
    print("Test 2: Accessing 'products' collection")
    print("="*60)
    products_ref = db.collection("products")
    
    print("Querying products collection...")
    try:
        # Try with limit first
        docs = list(products_ref.limit(10).stream())
        print(f"✓ Query successful: Found {len(docs)} products (limited to 10)")
        
        if len(docs) > 0:
            print("\nSample products:")
            for idx, doc in enumerate(docs[:3], 1):
                doc_data = doc.to_dict()
                title = doc_data.get('title', 'N/A')
                category = doc_data.get('categoryId', 'N/A')
                print(f"  {idx}. Title: {title}, Category: {category}")
        else:
            print("⚠ Collection appears empty or query returned no results")
            
            # Try without limit
            print("\nTrying without limit...")
            all_docs = list(products_ref.stream())
            print(f"  Total documents: {len(all_docs)}")
            
    except Exception as e:
        print(f"❌ Error querying products: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 3: Access categories collection
    print("\n" + "="*60)
    print("Test 3: Accessing 'categories' collection")
    print("="*60)
    categories_ref = db.collection("categories")
    
    print("Querying categories collection...")
    try:
        docs = list(categories_ref.stream())
        print(f"✓ Query successful: Found {len(docs)} categories")
        
        if len(docs) > 0:
            print("\nCategories found:")
            for idx, doc in enumerate(docs, 1):
                doc_data = doc.to_dict()
                cat_id = doc_data.get('categoryId') or doc_data.get('id') or doc.id
                name = doc_data.get('name') or doc_data.get('title') or 'N/A'
                print(f"  {idx}. ID: {cat_id}, Name: {name}")
        else:
            print("⚠ Collection appears empty")
            
    except Exception as e:
        print(f"❌ Error querying categories: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 4: Check permissions
    print("\n" + "="*60)
    print("Test 4: Verifying access method")
    print("="*60)
    print("✓ Using: google.cloud.firestore (Google Cloud Firestore client)")
    print("✓ NOT using: firebase_admin (Firebase Admin SDK)")
    print("✓ Authentication: Service Account credentials")
    print("✓ Access method: Direct Google Cloud API")
    
    print("\n" + "="*60)
    print("✅ All tests completed!")
    print("="*60)
    print("\nYou are accessing Firestore through Google Cloud, not Firebase Admin SDK.")
    print("If collections are empty, it means:")
    print("  1. The collections are actually empty in your database")
    print("  2. The service account doesn't have read permissions")
    print("  3. The collection names are different than expected")
    
except KeyboardInterrupt:
    print("\n\n⚠ Test interrupted by user")
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

