#!/usr/bin/env python
"""Simple script to list all collections in the 'trent' database"""
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
print("All Collections in 'trent' Database")
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
    
    print(f"Project: {project_id}")
    print(f"Database: 'trent'\n")
    
    # Import and connect
    from google.cloud import firestore
    from google.oauth2 import service_account
    
    credentials_obj = service_account.Credentials.from_service_account_info(
        service_account_dict
    )
    
    # Connect to 'trent' database
    db = firestore.Client(project=project_id, credentials=credentials_obj, database='trent')
    print("✓ Connected to Firestore\n")
    
    # List all collections
    print("Fetching collections...\n")
    collections = list(db.collections())
    
    if len(collections) > 0:
        print(f"Found {len(collections)} collections:\n")
        print("-" * 60)
        
        for idx, col in enumerate(collections, 1):
            collection_name = col.id
            print(f"\n{idx}. {collection_name}")
            
            # Get document count
            try:
                docs = list(col.stream())
                doc_count = len(docs)
                
                if doc_count > 0:
                    print(f"   ✓ Documents: {doc_count}")
                    
                    # Show sample fields from first document
                    if len(docs) > 0:
                        sample_doc = docs[0]
                        doc_data = sample_doc.to_dict()
                        fields = list(doc_data.keys())
                        print(f"   Fields: {', '.join(fields)}")
                else:
                    print(f"   ○ Documents: 0 (empty)")
            except Exception as e:
                print(f"   ⚠ Error counting documents: {e}")
        
        print("\n" + "-" * 60)
        print(f"\nTotal: {len(collections)} collections")
    else:
        print("⚠ No collections found in the database")
    
    # Print all documents in products collection
    print("\n" + "="*60)
    print("All Documents in 'products' Collection")
    print("="*60 + "\n")
    
    try:
        products_ref = db.collection("products")
        all_products = list(products_ref.stream())
        
        if len(all_products) > 0:
            print(f"Found {len(all_products)} products:\n")
            print("-" * 60)
            
            for idx, doc in enumerate(all_products, 1):
                doc_data = doc.to_dict()
                print(f"\n{idx}. Document ID: {doc.id}")
                
                # Print all fields
                for field_name, field_value in doc_data.items():
                    # Truncate long values for readability
                    value_str = str(field_value)
                    if len(value_str) > 100:
                        value_str = value_str[:100] + "..."
                    print(f"   {field_name}: {value_str}")
                
                print("-" * 60)
            
            print(f"\nTotal products: {len(all_products)}")
        else:
            print("⚠ No products found in the collection")
            
    except Exception as e:
        print(f"❌ Error reading products collection: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*60)
    print("✅ Done!")
    print("="*60)

except KeyboardInterrupt:
    print("\n\n⚠ Interrupted by user")
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

