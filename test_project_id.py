#!/usr/bin/env python
"""Test Firestore with the correct project ID"""
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
print("Testing Firestore with Project ID: 458510671023")
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
    print(f"Original project_id in credentials: {original_project_id}")
    print(f"Using project ID: 458510671023\n")
    
    # Import Google Cloud Firestore
    from google.cloud import firestore
    from google.oauth2 import service_account
    
    credentials_obj = service_account.Credentials.from_service_account_info(
        service_account_dict
    )
    
    # Try with the provided project ID
    db = firestore.Client(project="458510671023", credentials=credentials_obj)
    print("✓ Connected to Firestore with project ID: 458510671023\n")
    
    # Test collections
    print("="*60)
    print("Testing Collections")
    print("="*60)
    
    collections_to_test = ["products", "categories", "Products", "Categories"]
    
    for collection_name in collections_to_test:
        print(f"\nTesting '{collection_name}' collection:")
        try:
            col_ref = db.collection(collection_name)
            docs = list(col_ref.limit(10).stream())
            print(f"  ✓ Found {len(docs)} documents (showing first 10)")
            
            if len(docs) > 0:
                print(f"\n  Sample documents:")
                for idx, doc in enumerate(docs[:3], 1):
                    doc_data = doc.to_dict()
                    print(f"    {idx}. Document ID: {doc.id}")
                    print(f"       Fields: {list(doc_data.keys())}")
                    
                    # Show relevant fields
                    if 'title' in doc_data:
                        print(f"       Title: {doc_data['title']}")
                    if 'categoryId' in doc_data:
                        print(f"       CategoryId: {doc_data['categoryId']}")
                    if 'name' in doc_data:
                        print(f"       Name: {doc_data['name']}")
                    print()
                
                # Get total count
                all_docs = list(col_ref.stream())
                print(f"  Total documents in '{collection_name}': {len(all_docs)}")
                
                # If it's products, extract categoryIds
                if collection_name.lower() == "products":
                    category_ids = set()
                    for doc in all_docs:
                        doc_data = doc.to_dict()
                        if 'categoryId' in doc_data:
                            category_ids.add(doc_data['categoryId'])
                    if category_ids:
                        print(f"  Unique categoryIds found: {sorted(category_ids)}")
                
                # If it's categories, show all
                if collection_name.lower() in ["categories", "category"]:
                    print(f"\n  All categories:")
                    for doc in all_docs:
                        doc_data = doc.to_dict()
                        cat_id = doc_data.get('categoryId') or doc_data.get('id') or doc.id
                        name = doc_data.get('name') or doc_data.get('title') or 'N/A'
                        print(f"    - {cat_id}: {name}")
                
        except Exception as e:
            print(f"  ✗ Error: {e}")
    
    print("\n" + "="*60)
    print("✅ Test completed!")
    print("="*60)

except KeyboardInterrupt:
    print("\n\n⚠ Interrupted by user")
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

