#!/usr/bin/env python
"""Test script to list all collections and check categories"""
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
print("Testing Firebase Collections")
print("="*60 + "\n")

try:
    encoded_credentials = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")
    if not encoded_credentials:
        print("❌ ERROR: GOOGLE_APPLICATION_CREDENTIALS_JSON not found")
        sys.exit(1)
    
    json_credentials_str = base64.b64decode(encoded_credentials).decode("utf-8")
    service_account_dict = json.loads(json_credentials_str)
    project_id = service_account_dict.get('project_id')
    
    from google.cloud import firestore
    from google.oauth2 import service_account
    
    credentials_obj = service_account.Credentials.from_service_account_info(service_account_dict)
    db = firestore.Client(project=project_id, credentials=credentials_obj)
    print("✓ Connected to Firestore\n")
    
    # Test products collection
    print("1. Testing 'products' collection:")
    products_ref = db.collection("products")
    product_docs = list(products_ref.limit(5).stream())
    print(f"   Found {len(product_docs)} products (showing first 5)")
    if len(product_docs) > 0:
        # Show categoryIds from products
        category_ids_from_products = set()
        for doc in product_docs:
            doc_data = doc.to_dict()
            cat_id = doc_data.get('categoryId')
            if cat_id:
                category_ids_from_products.add(cat_id)
        print(f"   Unique categoryIds in products: {sorted(category_ids_from_products)}\n")
    
    # Test categories collection
    print("2. Testing 'categories' collection:")
    categories_ref = db.collection("categories")
    category_docs = list(categories_ref.stream())
    print(f"   Found {len(category_docs)} categories")
    
    if len(category_docs) > 0:
        print("   Categories:")
        for doc in category_docs:
            doc_data = doc.to_dict()
            print(f"     - ID: {doc.id}, Data: {list(doc_data.keys())}")
    else:
        print("   ⚠ Collection is empty or doesn't exist")
        print("   Checking if collection name might be different...\n")
        
        # Try alternative names
        alt_names = ['category', 'Category', 'Categories', 'CATEGORIES']
        for alt_name in alt_names:
            try:
                alt_ref = db.collection(alt_name)
                alt_docs = list(alt_ref.limit(1).stream())
                if len(alt_docs) > 0:
                    print(f"   ✓ Found collection '{alt_name}' with documents!")
                    break
            except:
                pass
    
    print("\n" + "="*60)
    print("Summary:")
    print(f"  - Products collection: {len(product_docs)} documents found")
    print(f"  - Categories collection: {len(category_docs)} documents found")
    if len(category_docs) == 0 and 'category_ids_from_products' in locals() and len(category_ids_from_products) > 0:
        print(f"\n  Note: Found {len(category_ids_from_products)} unique categoryIds in products")
        print("  You might want to use these categoryIds directly from products")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

