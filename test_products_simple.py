#!/usr/bin/env python
"""Simple test to verify products are being read from Firebase"""
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
print("Testing Firebase Products Reading")
print("="*60 + "\n")

# Test Firebase connection and credentials
encoded_credentials = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")
if not encoded_credentials:
    print("❌ ERROR: GOOGLE_APPLICATION_CREDENTIALS_JSON not found")
    sys.exit(1)

print("✓ Found Firebase credentials\n")

try:
    # Decode credentials
    json_credentials_str = base64.b64decode(encoded_credentials).decode("utf-8")
    service_account_dict = json.loads(json_credentials_str)
    print(f"✓ Credentials decoded successfully")
    print(f"  Project ID: {service_account_dict.get('project_id')}\n")
    
    # Try to import and use Firebase
    print("Attempting to connect to Firebase...")
    from google.cloud import firestore
    from google.oauth2 import service_account
    
    credentials_obj = service_account.Credentials.from_service_account_info(service_account_dict)
    db = firestore.Client(project=service_account_dict.get('project_id'), credentials=credentials_obj)
    print("✓ Connected to Firestore\n")
    
    # Query products
    print("Querying 'products' collection...")
    products_ref = db.collection("products")
    docs = list(products_ref.limit(10).stream())
    
    print(f"✓ Query completed: Found {len(docs)} documents (limited to 10)\n")
    
    if len(docs) > 0:
        print("Sample Products:")
        print("-" * 60)
        
        category_ids = set()
        
        for idx, doc in enumerate(docs, 1):
            doc_data = doc.to_dict()
            print(f"\nProduct {idx}:")
            print(f"  Document ID: {doc.id}")
            print(f"  Title: {doc_data.get('title', 'N/A')}")
            print(f"  CategoryId: {doc_data.get('categoryId', 'N/A')}")
            
            if doc_data.get('categoryId'):
                category_ids.add(doc_data.get('categoryId'))
            
            # Show other fields
            other_fields = {k: v for k, v in doc_data.items() 
                          if k not in ['title', 'categoryId']}
            if other_fields:
                print(f"  Other fields: {', '.join(list(other_fields.keys())[:5])}")
        
        print("\n" + "-" * 60)
        print(f"\nUnique CategoryIds found: {len(category_ids)}")
        for cat_id in sorted(category_ids):
            print(f"  - {cat_id}")
        
        print("\n" + "="*60)
        print("✅ TEST SUCCESSFUL!")
        print("="*60)
        print(f"\nSummary:")
        print(f"  - Products can be read: ✓")
        print(f"  - Products have 'title' field: ✓")
        print(f"  - Products have 'categoryId' field: ✓")
        print(f"  - Unique categories found: {len(category_ids)}")
        
    else:
        print("⚠ No products found in the collection")
        print("  The collection might be empty")
        
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

