#!/usr/bin/env python
"""Quick test to read products collection"""
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
print("Quick Test: Reading Products Collection")
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
    
    # Import and connect
    from google.cloud import firestore
    from google.oauth2 import service_account
    
    credentials_obj = service_account.Credentials.from_service_account_info(
        service_account_dict
    )
    db = firestore.Client(project=project_id, credentials=credentials_obj)
    print("✓ Connected to Firestore\n")
    
    # Read products collection
    print("Reading 'products' collection...")
    products_ref = db.collection("products")
    
    # Get all products
    all_docs = list(products_ref.stream())
    total = len(all_docs)
    
    print(f"\n✓ Total products found: {total}\n")
    
    if total > 0:
        print("="*60)
        print("Products:")
        print("="*60)
        
        for idx, doc in enumerate(all_docs, 1):
            doc_data = doc.to_dict()
            title = doc_data.get('title', 'N/A')
            category_id = doc_data.get('categoryId', 'N/A')
            price = doc_data.get('price', 'N/A')
            status = doc_data.get('status', 'N/A')
            
            print(f"\n{idx}. Document ID: {doc.id}")
            print(f"   Title: {title}")
            print(f"   CategoryId: {category_id}")
            print(f"   Price: {price}")
            print(f"   Status: {status}")
            
            # Show all available fields
            all_fields = list(doc_data.keys())
            if len(all_fields) > 4:
                print(f"   All fields: {', '.join(all_fields)}")
        
        print("\n" + "="*60)
        print("✅ SUCCESS! Products found and displayed!")
        print("="*60)
        
        # Extract unique categoryIds
        category_ids = set()
        for doc in all_docs:
            doc_data = doc.to_dict()
            if 'categoryId' in doc_data and doc_data['categoryId']:
                category_ids.add(doc_data['categoryId'])
        
        if category_ids:
            print(f"\nUnique CategoryIds found: {sorted(category_ids)}")
    else:
        print("⚠ No products found in the collection")
        print("\nThe collection exists but is empty.")
        print("Possible reasons:")
        print("  1. Data hasn't been added yet")
        print("  2. Data is in a different collection name")
        print("  3. Security rules are blocking reads")
        print("  4. Data is in a different database instance")

except KeyboardInterrupt:
    print("\n\n⚠ Interrupted by user")
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

