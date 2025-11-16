#!/usr/bin/env python
"""Find which database has the products data"""
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
print("Finding Database with Products Data")
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
    
    credentials_obj = service_account.Credentials.from_service_account_info(
        service_account_dict
    )
    
    # List databases
    try:
        from google.cloud.firestore_admin_v1 import FirestoreAdminClient
        
        admin_client = FirestoreAdminClient(credentials=credentials_obj)
        parent = f"projects/{project_id}"
        response = admin_client.list_databases(parent=parent)
        databases = response.databases
        
        print(f"Found {len(databases)} databases:\n")
        
        found_data = False
        
        for db_info in databases:
            db_name = db_info.name.split('/')[-1]
            location = db_info.location_id if hasattr(db_info, 'location_id') else 'N/A'
            
            print(f"Testing database: {db_name} (Location: {location})")
            
            # Create client for this database
            if db_name == '(default)':
                db = firestore.Client(project=project_id, credentials=credentials_obj)
            else:
                db = firestore.Client(
                    project=project_id, 
                    credentials=credentials_obj,
                    database=db_name
                )
            
            # Test products collection
            try:
                products_ref = db.collection("products")
                docs = list(products_ref.limit(10).stream())
                
                if len(docs) > 0:
                    print(f"  ✅ FOUND {len(docs)} PRODUCTS IN DATABASE: '{db_name}'!\n")
                    found_data = True
                    
                    # Show sample products
                    print("  Sample products:")
                    for idx, doc in enumerate(docs[:5], 1):
                        doc_data = doc.to_dict()
                        title = doc_data.get('title', 'N/A')
                        category = doc_data.get('categoryId', 'N/A')
                        print(f"    {idx}. {title} (Category: {category})")
                    
                    # Get total count
                    all_docs = list(products_ref.stream())
                    print(f"\n  Total products: {len(all_docs)}")
                    
                    # Test categories
                    categories_ref = db.collection("categories")
                    cat_docs = list(categories_ref.limit(10).stream())
                    if len(cat_docs) > 0:
                        print(f"\n  ✅ Found {len(cat_docs)} categories:")
                        for doc in cat_docs:
                            doc_data = doc.to_dict()
                            cat_id = doc_data.get('categoryId') or doc_data.get('id') or doc.id
                            name = doc_data.get('name') or doc_data.get('title') or 'N/A'
                            print(f"    - {cat_id}: {name}")
                    
                    print("\n" + "="*60)
                    print(f"✅ SUCCESS! Data found in database: '{db_name}'")
                    print("="*60)
                    print(f"\nDatabase name to use: {db_name}")
                    if db_name != '(default)':
                        print(f"\nWe need to update the code to use database='{db_name}'")
                    break
                else:
                    print(f"  ○ No products found (0 documents)\n")
                    
            except Exception as e:
                print(f"  ✗ Error: {e}\n")
        
        if not found_data:
            print("⚠ No products found in any database")
            print("Please verify the data exists in Firebase Console")
            
    except ImportError:
        print("⚠ Admin API not available, testing common database names...")
        # Fallback to testing common names
        for db_name in ['(default)', 'default', 'main']:
            try:
                if db_name == '(default)':
                    db = firestore.Client(project=project_id, credentials=credentials_obj)
                else:
                    db = firestore.Client(project=project_id, credentials=credentials_obj, database=db_name)
                
                products_ref = db.collection("products")
                docs = list(products_ref.limit(5).stream())
                if len(docs) > 0:
                    print(f"✅ Found data in '{db_name}'!")
                    break
            except:
                pass
    except Exception as e:
        print(f"✗ Error listing databases: {e}")
        import traceback
        traceback.print_exc()

except KeyboardInterrupt:
    print("\n\n⚠ Interrupted")
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

