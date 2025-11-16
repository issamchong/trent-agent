#!/usr/bin/env python
"""Check if service account can access the target project"""
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
print("Checking Project Access")
print("="*60 + "\n")

project_number = "458510671023"

try:
    # Get credentials
    encoded_credentials = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")
    if not encoded_credentials:
        print("❌ ERROR: GOOGLE_APPLICATION_CREDENTIALS_JSON not found")
        sys.exit(1)
    
    # Decode credentials
    json_credentials_str = base64.b64decode(encoded_credentials).decode("utf-8")
    service_account_dict = json.loads(json_credentials_str)
    
    current_project_id = service_account_dict.get('project_id')
    print(f"Current Service Account Project: {current_project_id}")
    print(f"Target Project Number: {project_number}\n")
    
    # Try to resolve project ID
    print("="*60)
    print("Attempting to resolve project ID from project number...")
    print("="*60)
    
    try:
        from google.cloud import resourcemanager_v3
        from google.oauth2 import service_account
        
        credentials_obj = service_account.Credentials.from_service_account_info(
            service_account_dict
        )
        
        client = resourcemanager_v3.ProjectsClient(credentials=credentials_obj)
        
        # Try to get project by number
        try:
            project_name = f"projects/{project_number}"
            project = client.get_project(name=project_name)
            resolved_project_id = project.project_id
            print(f"✓ SUCCESS! Resolved project ID: {resolved_project_id}")
            print(f"  Project Name: {project.display_name}")
            print(f"  Project Number: {project_number}")
            print(f"  Project ID: {resolved_project_id}\n")
            
            # Now test Firestore access with resolved project ID
            print("="*60)
            print("Testing Firestore Access with Resolved Project ID")
            print("="*60)
            
            from google.cloud import firestore
            
            db = firestore.Client(project=resolved_project_id, credentials=credentials_obj)
            print(f"✓ Connected to Firestore with project: {resolved_project_id}\n")
            
            # Test products collection
            print("Testing 'products' collection:")
            products_ref = db.collection("products")
            docs = list(products_ref.limit(10).stream())
            print(f"  ✓ Found {len(docs)} products (showing first 10)")
            
            if len(docs) > 0:
                print("\n  ✓ SUCCESS! Products found!")
                for idx, doc in enumerate(docs[:3], 1):
                    doc_data = doc.to_dict()
                    title = doc_data.get('title', 'N/A')
                    category = doc_data.get('categoryId', 'N/A')
                    print(f"    {idx}. {title} (Category: {category})")
                
                # Get total count
                all_docs = list(products_ref.stream())
                print(f"\n  Total products: {len(all_docs)}")
            else:
                print("  ⚠ Collection exists but is empty")
            
            # Test categories collection
            print("\nTesting 'categories' collection:")
            categories_ref = db.collection("categories")
            docs = list(categories_ref.limit(10).stream())
            print(f"  ✓ Found {len(docs)} categories (showing first 10)")
            
            if len(docs) > 0:
                print("\n  ✓ SUCCESS! Categories found!")
                for idx, doc in enumerate(docs, 1):
                    doc_data = doc.to_dict()
                    cat_id = doc_data.get('categoryId') or doc_data.get('id') or doc.id
                    name = doc_data.get('name') or doc_data.get('title') or 'N/A'
                    print(f"    {idx}. {cat_id}: {name}")
            else:
                print("  ⚠ Collection exists but is empty")
            
            print("\n" + "="*60)
            print("✅ SUCCESS! Project ID resolved and data accessible!")
            print("="*60)
            print(f"\nProject ID to use: {resolved_project_id}")
            print("We can now update the code to use this project ID.")
            
        except Exception as e:
            print(f"✗ Could not resolve project: {e}")
            print("\nPossible reasons:")
            print("  1. Service account doesn't have access to that project")
            print("  2. Project number is incorrect")
            print("  3. Need a service account for that specific project")
            
    except ImportError:
        print("⚠ google-cloud-resource-manager not available")
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
    
except KeyboardInterrupt:
    print("\n\n⚠ Interrupted by user")
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

