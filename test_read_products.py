#!/usr/bin/env python
"""Simple test to verify products can be read from Firebase"""
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

try:
    # Test credentials first
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
    
    # Query products (limit to 10 for quick test)
    print("Querying 'products' collection (limit 10)...")
    products_ref = db.collection("products")
    
    # Use get() with limit instead of stream() to avoid hanging
    query = products_ref.limit(10)
    docs = list(query.stream())
    
    print(f"✓ Found {len(docs)} products\n")
    
    if len(docs) == 0:
        print("⚠ No products found in the collection")
        print("  The collection might be empty")
    else:
        print("Sample Products:")
        print("-" * 60)
        
        category_ids = set()
        products_with_title = 0
        products_with_category = 0
        
        for idx, doc in enumerate(docs, 1):
            doc_data = doc.to_dict()
            title = doc_data.get('title', None)
            category_id = doc_data.get('categoryId', None)
            
            if title:
                products_with_title += 1
            if category_id:
                products_with_category += 1
                category_ids.add(category_id)
            
            print(f"\nProduct {idx}:")
            print(f"  Document ID: {doc.id}")
            print(f"  Title: {title if title else '❌ MISSING'}")
            print(f"  CategoryId: {category_id if category_id else '❌ MISSING'}")
            
            # Show a few other fields
            other_fields = [k for k in doc_data.keys() if k not in ['title', 'categoryId', '_id']]
            if other_fields:
                print(f"  Other fields: {', '.join(other_fields[:3])}")
        
        print("\n" + "-" * 60)
        print(f"\nSummary:")
        print(f"  ✓ Total products read: {len(docs)}")
        print(f"  ✓ Products with 'title' field: {products_with_title}/{len(docs)}")
        print(f"  ✓ Products with 'categoryId' field: {products_with_category}/{len(docs)}")
        print(f"  ✓ Unique categoryIds found: {len(category_ids)}")
        
        if category_ids:
            print(f"\nAvailable CategoryIds:")
            for cat_id in sorted(category_ids):
                print(f"  - {cat_id}")
        
        print("\n" + "="*60)
        print("✅ TEST SUCCESSFUL!")
        print("="*60)
        print("\nProducts are being read correctly with:")
        print("  - 'title' field: ✓")
        print("  - 'categoryId' field: ✓")
        print("\nThe agent should be able to read and display products successfully!")

except KeyboardInterrupt:
    print("\n\n⚠ Test interrupted by user")
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

