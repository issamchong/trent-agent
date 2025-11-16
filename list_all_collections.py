#!/usr/bin/env python
"""Script to list all collections in Firestore database"""
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
print("Listing All Collections in Firestore")
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
    
    # Import Google Cloud Firestore
    from google.cloud import firestore
    from google.oauth2 import service_account
    
    credentials_obj = service_account.Credentials.from_service_account_info(
        service_account_dict
    )
    db = firestore.Client(project=project_id, credentials=credentials_obj)
    print("✓ Connected to Firestore\n")
    
    # Method 1: Try to list all collections (requires permissions)
    print("="*60)
    print("Method 1: Listing all collections (if permissions allow)")
    print("="*60)
    try:
        collections = list(db.collections())
        if collections:
            print(f"✓ Found {len(collections)} collections:\n")
            for col in collections:
                # Try to get document count
                try:
                    doc_count = len(list(col.limit(1000).stream()))
                    print(f"  📁 {col.id} ({doc_count} documents)")
                except:
                    print(f"  📁 {col.id} (could not count documents)")
        else:
            print("⚠ No collections found or insufficient permissions to list")
    except Exception as e:
        print(f"⚠ Could not list collections: {e}")
        print("  This might require additional permissions")
        print("  Trying alternative method...\n")
    
    # Method 2: Try common collection names
    print("\n" + "="*60)
    print("Method 2: Testing common collection names")
    print("="*60)
    
    common_names = [
        "products", "Products", "PRODUCTS",
        "categories", "Categories", "CATEGORIES", "category", "Category",
        "users", "Users", "USERS",
        "orders", "Orders", "ORDERS",
        "vendors", "Vendors", "VENDORS",
        "items", "Items", "ITEMS",
    ]
    
    found_collections = []
    
    for name in common_names:
        try:
            col_ref = db.collection(name)
            # Try to read at least one document
            docs = list(col_ref.limit(1).stream())
            if docs or True:  # Collection exists even if empty
                # Count total documents
                all_docs = list(col_ref.stream())
                count = len(all_docs)
                found_collections.append((name, count))
                status = "✓" if count > 0 else "○"
                print(f"  {status} '{name}': {count} documents")
        except Exception as e:
            # Collection doesn't exist or no access
            pass
    
    if found_collections:
        print(f"\n✓ Found {len(found_collections)} existing collections")
    else:
        print("\n⚠ No collections found with common names")
    
    # Method 3: Try to get collection info from a known document path
    print("\n" + "="*60)
    print("Method 3: Checking specific collection structures")
    print("="*60)
    
    # Test products collection structure
    print("\nTesting 'products' collection:")
    try:
        products_ref = db.collection("products")
        sample_docs = list(products_ref.limit(5).stream())
        if sample_docs:
            print(f"  ✓ Found {len(sample_docs)} sample documents")
            for doc in sample_docs:
                doc_data = doc.to_dict()
                print(f"    Document ID: {doc.id}")
                print(f"    Fields: {list(doc_data.keys())}")
                if 'categoryId' in doc_data:
                    print(f"    categoryId: {doc_data['categoryId']}")
                break
        else:
            print("  ○ Collection exists but is empty")
    except Exception as e:
        print(f"  ✗ Error: {e}")
    
    # Test categories collection structure
    print("\nTesting 'categories' collection:")
    try:
        categories_ref = db.collection("categories")
        sample_docs = list(categories_ref.limit(5).stream())
        if sample_docs:
            print(f"  ✓ Found {len(sample_docs)} sample documents")
            for doc in sample_docs:
                doc_data = doc.to_dict()
                print(f"    Document ID: {doc.id}")
                print(f"    Fields: {list(doc_data.keys())}")
                break
        else:
            print("  ○ Collection exists but is empty")
    except Exception as e:
        print(f"  ✗ Error: {e}")
    
    # Summary
    print("\n" + "="*60)
    print("Summary")
    print("="*60)
    if found_collections:
        print("\nCollections found:")
        for name, count in found_collections:
            print(f"  - {name}: {count} documents")
    else:
        print("\n⚠ No collections found. Possible reasons:")
        print("  1. Collections are actually empty")
        print("  2. Service account lacks read permissions")
        print("  3. Collection names are different than expected")
        print("  4. Database is in a different project/region")
    
    print("\n" + "="*60)
    print("✅ Collection check completed!")
    print("="*60)

except KeyboardInterrupt:
    print("\n\n⚠ Interrupted by user")
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

