#!/usr/bin/env python
"""Check for multiple Firestore databases"""
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
print("Checking for Multiple Firestore Databases")
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
    
    from google.cloud import firestore
    from google.oauth2 import service_account
    
    credentials_obj = service_account.Credentials.from_service_account_info(
        service_account_dict
    )
    
    # Try to list databases using Firestore Admin API
    print("="*60)
    print("Method 1: Using Firestore Admin API to list databases")
    print("="*60)
    
    try:
        from google.cloud.firestore_admin_v1 import FirestoreAdminClient
        from google.cloud.firestore_admin_v1.types import ListDatabasesRequest
        
        admin_client = FirestoreAdminClient(credentials=credentials_obj)
        parent = f"projects/{project_id}"
        
        try:
            response = admin_client.list_databases(parent=parent)
            databases = response.databases
            
            print(f"✓ Found {len(databases)} databases:\n")
            
            for db_info in databases:
                db_name = db_info.name.split('/')[-1]  # Extract database name
                db_type = db_info.type_.name if hasattr(db_info, 'type_') else 'UNKNOWN'
                location = db_info.location_id if hasattr(db_info, 'location_id') else 'N/A'
                
                print(f"  Database: {db_name}")
                print(f"    Type: {db_type}")
                print(f"    Location: {location}")
                
                # Try to access this database
                if db_name == '(default)':
                    db = firestore.Client(project=project_id, credentials=credentials_obj)
                else:
                    # Try with database name
                    try:
                        db = firestore.Client(
                            project=project_id, 
                            credentials=credentials_obj,
                            database=db_name
                        )
                    except:
                        print(f"    ⚠ Could not create client for {db_name}")
                        continue
                
                # Test products collection in this database
                try:
                    products_ref = db.collection("products")
                    docs = list(products_ref.limit(5).stream())
                    status = "✓" if len(docs) > 0 else "○"
                    print(f"    {status} Products: {len(docs)} documents")
                    
                    if len(docs) > 0:
                        print(f"    ✅ FOUND DATA IN DATABASE: {db_name}!")
                        for doc in docs[:2]:
                            doc_data = doc.to_dict()
                            print(f"      - {doc.id}: {doc_data.get('title', 'N/A')}")
                except Exception as e:
                    print(f"    ✗ Error accessing products: {e}")
                
                print()
                
        except Exception as e:
            print(f"✗ Could not list databases: {e}")
            print("  This might require 'Cloud Datastore Admin' role")
            
    except ImportError:
        print("⚠ google-cloud-firestore-admin not installed")
        print("  Install with: pip install google-cloud-firestore-admin")
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
    
    # Method 2: Try common database names
    print("="*60)
    print("Method 2: Testing Common Database Names")
    print("="*60)
    
    common_db_names = ['(default)', 'default', 'main', 'production', 'prod', 'dev', 'development']
    
    for db_name in common_db_names:
        try:
            if db_name == '(default)':
                db = firestore.Client(project=project_id, credentials=credentials_obj)
            else:
                db = firestore.Client(
                    project=project_id, 
                    credentials=credentials_obj,
                    database=db_name
                )
            
            products_ref = db.collection("products")
            docs = list(products_ref.limit(5).stream())
            
            if len(docs) > 0:
                print(f"\n✅ FOUND DATA IN DATABASE: '{db_name}'!")
                print(f"   Found {len(docs)} products (showing first 5)")
                for doc in docs:
                    doc_data = doc.to_dict()
                    print(f"     - {doc.id}: {doc_data.get('title', 'N/A')}")
                break
            else:
                print(f"  ○ '{db_name}': 0 documents")
        except Exception as e:
            print(f"  ✗ '{db_name}': Error - {e}")
    
    print("\n" + "="*60)
    print("Next Steps")
    print("="*60)
    print("\nIf data was found above, note the database name.")
    print("We'll need to update the code to use that specific database.")
    print("\nIf no data was found:")
    print("  1. Check Firebase Console for the exact database name")
    print("  2. Verify the collection name matches exactly")
    print("  3. Check if you're looking at the correct project")

except KeyboardInterrupt:
    print("\n\n⚠ Interrupted by user")
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

