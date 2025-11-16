#!/usr/bin/env python
"""Resolve project ID from project number and test access"""
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
print("Resolving Project ID from Project Number")
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
    print(f"Current service account project_id: {current_project_id}")
    print(f"Target project number: {project_number}\n")
    
    # Try to resolve project ID using Resource Manager API
    print("="*60)
    print("Attempting to resolve project ID...")
    print("="*60)
    
    try:
        from google.cloud import resourcemanager_v3
        from google.oauth2 import service_account
        
        credentials_obj = service_account.Credentials.from_service_account_info(
            service_account_dict
        )
        
        # Try to get project info
        client = resourcemanager_v3.ProjectsClient(credentials=credentials_obj)
        project_name = f"projects/{project_number}"
        
        try:
            project = client.get_project(name=project_name)
            resolved_project_id = project.project_id
            print(f"✓ Resolved project ID: {resolved_project_id}")
            print(f"  Project Name: {project.display_name}")
            print(f"  Project Number: {project_number}")
        except Exception as e:
            print(f"⚠ Could not resolve via Resource Manager: {e}")
            print("  This might require additional permissions")
            resolved_project_id = None
            
    except ImportError:
        print("⚠ google-cloud-resource-manager not installed")
        print("  Install with: pip install google-cloud-resource-manager")
        resolved_project_id = None
    except Exception as e:
        print(f"⚠ Error accessing Resource Manager: {e}")
        resolved_project_id = None
    
    # Alternative: Try common project ID patterns
    if not resolved_project_id:
        print("\nTrying alternative methods...")
        print("Note: You may need to provide the project ID manually")
        print("Common patterns:")
        print("  - Check Firebase Console for the project ID")
        print("  - Check Google Cloud Console")
        print("  - Project ID is usually alphanumeric (e.g., 'my-project-123')")
    
    # Test Firestore access with project number (sometimes works)
    print("\n" + "="*60)
    print("Testing Firestore Access")
    print("="*60)
    
    from google.cloud import firestore
    from google.oauth2 import service_account
    
    credentials_obj = service_account.Credentials.from_service_account_info(
        service_account_dict
    )
    
    # Test 1: Try with project number directly
    print("\n1. Testing with project number as project ID:")
    try:
        db1 = firestore.Client(project=project_number, credentials=credentials_obj)
        products_ref = db1.collection("products")
        docs = list(products_ref.limit(5).stream())
        print(f"   ✓ Connected! Found {len(docs)} products")
        if len(docs) > 0:
            print("   ✓ SUCCESS! Data found!")
            for doc in docs[:2]:
                doc_data = doc.to_dict()
                print(f"     - {doc.id}: {doc_data.get('title', 'N/A')}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test 2: If we resolved project ID, try with that
    if resolved_project_id:
        print(f"\n2. Testing with resolved project ID '{resolved_project_id}':")
        try:
            db2 = firestore.Client(project=resolved_project_id, credentials=credentials_obj)
            products_ref = db2.collection("products")
            docs = list(products_ref.limit(5).stream())
            print(f"   ✓ Connected! Found {len(docs)} products")
            if len(docs) > 0:
                print("   ✓ SUCCESS! Data found!")
        except Exception as e:
            print(f"   ✗ Error: {e}")
    
    # Test 3: Current project
    print(f"\n3. Testing with current project '{current_project_id}':")
    try:
        db3 = firestore.Client(project=current_project_id, credentials=credentials_obj)
        products_ref = db3.collection("products")
        docs = list(products_ref.limit(5).stream())
        print(f"   Found {len(docs)} products")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    print("\n" + "="*60)
    print("Summary")
    print("="*60)
    print(f"\nProject Number: {project_number}")
    if resolved_project_id:
        print(f"Resolved Project ID: {resolved_project_id}")
    else:
        print("Project ID: Not resolved (please provide manually)")
    print(f"\nCurrent Service Account Project: {current_project_id}")
    print("\nNext Steps:")
    print("1. If data was found above, we can update the code to use that project")
    print("2. If not, please provide the project ID from Firebase Console")
    print("3. Or provide a service account JSON for the correct project")
    
except KeyboardInterrupt:
    print("\n\n⚠ Interrupted by user")
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

