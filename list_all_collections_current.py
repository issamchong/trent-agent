#!/usr/bin/env python
"""List all collections in the current database (trent)"""
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
print("Listing All Collections in Current Database")
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
    
    print(f"Project ID: {project_id}")
    print(f"Database: 'trent'\n")
    
    # Import and connect
    from google.cloud import firestore
    from google.oauth2 import service_account
    
    credentials_obj = service_account.Credentials.from_service_account_info(
        service_account_dict
    )
    
    # Connect to 'trent' database (current configuration)
    db = firestore.Client(project=project_id, credentials=credentials_obj, database='trent')
    print("✓ Connected to 'trent' database\n")
    
    # List all collections
    print("="*60)
    print("All Collections:")
    print("="*60)
    
    try:
        collections = list(db.collections())
        
        if len(collections) > 0:
            print(f"\n✓ Found {len(collections)} collections:\n")
            
            for idx, col in enumerate(collections, 1):
                collection_name = col.id
                print(f"{idx}. Collection: {collection_name}")
                
                # Get document count
                try:
                    docs = list(col.limit(1000).stream())
                    doc_count = len(docs)
                    
                    if doc_count > 0:
                        print(f"   ✓ Documents: {doc_count}")
                        
                        # Show sample document structure
                        if len(docs) > 0:
                            sample_doc = docs[0]
                            doc_data = sample_doc.to_dict()
                            fields = list(doc_data.keys())
                            print(f"   Fields: {', '.join(fields[:10])}{'...' if len(fields) > 10 else ''}")
                            
                            # Show a few sample values for key fields
                            if 'title' in doc_data:
                                print(f"   Sample title: {doc_data['title']}")
                            if 'name' in doc_data:
                                print(f"   Sample name: {doc_data['name']}")
                            if 'categoryId' in doc_data:
                                print(f"   Sample categoryId: {doc_data['categoryId']}")
                    else:
                        print(f"   ○ Documents: 0 (empty)")
                    
                except Exception as e:
                    print(f"   ⚠ Could not count documents: {e}")
                
                print()
        else:
            print("⚠ No collections found")
            print("\nPossible reasons:")
            print("  1. Collections are empty")
            print("  2. Insufficient permissions to list collections")
            print("  3. Database is empty")
            
    except Exception as e:
        print(f"✗ Error listing collections: {e}")
        print("\nTrying alternative method...")
        
        # Alternative: Try to access known collections
        known_collections = ['products', 'categories', 'users', 'orders', 'vendors']
        print("\nTesting known collection names:")
        for col_name in known_collections:
            try:
                col_ref = db.collection(col_name)
                docs = list(col_ref.limit(1).stream())
                if docs or True:  # Collection exists even if empty
                    all_docs = list(col_ref.stream())
                    status = "✓" if len(all_docs) > 0 else "○"
                    print(f"  {status} {col_name}: {len(all_docs)} documents")
            except:
                pass
    
    print("="*60)
    print("✅ Collection listing completed!")
    print("="*60)

except KeyboardInterrupt:
    print("\n\n⚠ Interrupted by user")
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

