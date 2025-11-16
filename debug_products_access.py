#!/usr/bin/env python
"""Debug why products collection shows 0 documents when data exists"""
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
print("Debugging Products Collection Access")
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
    client_email = service_account_dict.get('client_email')
    
    print(f"Project ID: {project_id}")
    print(f"Service Account: {client_email}\n")
    
    # Import and connect
    from google.cloud import firestore
    from google.oauth2 import service_account
    
    credentials_obj = service_account.Credentials.from_service_account_info(
        service_account_dict
    )
    
    # Test 1: Default database
    print("="*60)
    print("Test 1: Default Database")
    print("="*60)
    try:
        db = firestore.Client(project=project_id, credentials=credentials_obj)
        print("✓ Connected to default database")
        
        products_ref = db.collection("products")
        
        # Try different query methods
        print("\n1.1. Using stream() without limit:")
        try:
            docs = list(products_ref.stream())
            print(f"   Result: {len(docs)} documents")
            if len(docs) > 0:
                print(f"   ✓ FOUND {len(docs)} DOCUMENTS!")
                for doc in docs[:3]:
                    print(f"     - {doc.id}: {doc.to_dict().get('title', 'N/A')}")
        except Exception as e:
            print(f"   ✗ Error: {e}")
        
        print("\n1.2. Using stream() with limit(100):")
        try:
            docs = list(products_ref.limit(100).stream())
            print(f"   Result: {len(docs)} documents")
        except Exception as e:
            print(f"   ✗ Error: {e}")
        
        print("\n1.3. Trying to get collection info:")
        try:
            # Try to access collection metadata
            print(f"   Collection path: products")
            # Try to get a specific document by common ID
            test_ids = ["1", "product1", "test", "sample", "prod1"]
            for test_id in test_ids:
                doc_ref = products_ref.document(test_id)
                doc = doc_ref.get()
                if doc.exists:
                    print(f"   ✓ Found document '{test_id}': {doc.to_dict()}")
                    break
        except Exception as e:
            print(f"   Error checking specific documents: {e}")
        
    except Exception as e:
        print(f"✗ Error connecting: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 2: Check if we need to specify database
    print("\n" + "="*60)
    print("Test 2: Checking Database Configuration")
    print("="*60)
    print("Firestore supports multiple databases per project.")
    print("The default database is usually '(default)'")
    print("\nIf you have multiple databases, you may need to specify the database name.")
    
    # Test 3: Try with explicit database parameter (if supported)
    print("\n" + "="*60)
    print("Test 3: Testing Database Parameter")
    print("="*60)
    try:
        # Check Firestore client version and capabilities
        print(f"Firestore client version: {firestore.__version__ if hasattr(firestore, '__version__') else 'unknown'}")
        
        # Try to create client with database parameter
        # Note: This might require a specific version or method
        try:
            # Some versions support database parameter in Client constructor
            db_with_db = firestore.Client(
                project=project_id, 
                credentials=credentials_obj,
                database='(default)'  # Try default database name
            )
            print("✓ Created client with explicit database='(default)'")
            
            products_ref = db_with_db.collection("products")
            docs = list(products_ref.limit(10).stream())
            print(f"   Found {len(docs)} documents")
            if len(docs) > 0:
                print("   ✓ SUCCESS! Documents found with explicit database!")
        except TypeError:
            print("   Database parameter not supported in this version")
        except Exception as e:
            print(f"   Error: {e}")
            
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 4: Check permissions and security
    print("\n" + "="*60)
    print("Test 4: Permission Check")
    print("="*60)
    print("If documents exist but aren't accessible, possible reasons:")
    print("  1. Security rules are blocking reads")
    print("  2. Service account lacks 'Cloud Datastore User' role")
    print("  3. Data is in a different database instance")
    print("  4. Data is in a different region")
    
    # Test write to verify permissions
    try:
        test_collection = db.collection("_test_debug")
        test_doc_ref = test_collection.document("permission_test")
        test_doc_ref.set({"test": True, "timestamp": "debug"})
        test_doc = test_doc_ref.get()
        if test_doc.exists:
            print("   ✓ Write permission: OK")
            test_doc_ref.delete()
        else:
            print("   ✗ Write permission: Failed")
    except Exception as e:
        print(f"   ⚠ Write test error: {e}")
    
    # Test 5: List all collections (if possible)
    print("\n" + "="*60)
    print("Test 5: Collection Discovery")
    print("="*60)
    try:
        # Try to list collections (requires permissions)
        collections = list(db.collections())
        print(f"   Found {len(collections)} collections:")
        for col in collections[:10]:
            try:
                count = len(list(col.limit(1000).stream()))
                status = "✓" if count > 0 else "○"
                print(f"     {status} {col.id}: {count} documents")
            except:
                print(f"     ? {col.id}: (could not count)")
    except Exception as e:
        print(f"   Could not list collections: {e}")
        print("   (This might require additional permissions)")
    
    print("\n" + "="*60)
    print("Summary & Recommendations")
    print("="*60)
    print("\nIf documents exist in Firebase Console but aren't showing here:")
    print("  1. Check Firestore Security Rules in Firebase Console")
    print("  2. Verify service account has proper IAM roles")
    print("  3. Check if you have multiple Firestore databases")
    print("  4. Verify you're looking at the correct project")
    print("  5. Check if data is in a different region")
    
    print("\nTo check in Firebase Console:")
    print("  1. Go to Firebase Console → Firestore Database")
    print("  2. Check the database name (might not be 'default')")
    print("  3. Verify the collection name matches exactly")
    print("  4. Check Security Rules tab")

except KeyboardInterrupt:
    print("\n\n⚠ Interrupted by user")
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

