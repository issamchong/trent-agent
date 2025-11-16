#!/usr/bin/env python
"""Test script to verify categories collection can be read"""
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
print("Testing Firebase Categories Collection Reading")
print("="*60 + "\n")

try:
    # Test credentials
    encoded_credentials = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")
    if not encoded_credentials:
        print("❌ ERROR: GOOGLE_APPLICATION_CREDENTIALS_JSON not found")
        sys.exit(1)
    
    print("✓ Firebase credentials found")
    
    # Decode and verify
    json_credentials_str = base64.b64decode(encoded_credentials).decode("utf-8")
    service_account_dict = json.loads(json_credentials_str)
    project_id = service_account_dict.get('project_id')
    print(f"✓ Project ID: {project_id}\n")
    
    # Import Firebase
    print("Connecting to Firebase...")
    from google.cloud import firestore
    from google.oauth2 import service_account
    
    credentials_obj = service_account.Credentials.from_service_account_info(service_account_dict)
    db = firestore.Client(project=project_id, credentials=credentials_obj)
    print("✓ Connected to Firestore\n")
    
    # Query categories collection
    print("Querying 'categories' collection...")
    categories_ref = db.collection("categories")
    docs = list(categories_ref.stream())
    
    print(f"✓ Found {len(docs)} categories\n")
    
    if len(docs) == 0:
        print("⚠ No categories found in the collection")
        print("  The collection might be empty or doesn't exist")
    else:
        print("Categories Found:")
        print("-" * 60)
        
        category_ids = []
        
        for idx, doc in enumerate(docs, 1):
            doc_data = doc.to_dict()
            category_id = doc_data.get('categoryId') or doc_data.get('id') or doc.id
            name = doc_data.get('name') or doc_data.get('title') or 'N/A'
            
            category_ids.append(category_id)
            
            print(f"\nCategory {idx}:")
            print(f"  Document ID: {doc.id}")
            print(f"  CategoryId: {category_id}")
            print(f"  Name: {name}")
            
            # Show all fields
            all_fields = list(doc_data.keys())
            if all_fields:
                print(f"  All fields: {', '.join(all_fields)}")
                # Show a few field values
                for field in ['description', 'image', 'icon']:
                    if field in doc_data:
                        value = str(doc_data[field])[:50]
                        print(f"  {field}: {value}")
        
        print("\n" + "-" * 60)
        print(f"\nSummary:")
        print(f"  ✓ Total categories: {len(docs)}")
        print(f"  ✓ CategoryIds found: {len(category_ids)}")
        
        if category_ids:
            print(f"\nAvailable CategoryIds:")
            for cat_id in category_ids:
                print(f"  - {cat_id}")
        
        print("\n" + "="*60)
        print("✅ TEST SUCCESSFUL!")
        print("="*60)
        print("\nCategories collection is being read correctly!")
        print("The agent can now query this collection to show available categories to users.")

except KeyboardInterrupt:
    print("\n\n⚠ Test interrupted by user")
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

