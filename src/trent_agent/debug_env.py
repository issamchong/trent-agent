# debug_env.py
import os
import base64
import json

print("--- Starting Environment Variable Diagnostic ---")

# This mimics what your Firebase tool does
encoded_credentials = os.getenv('GOOGLE_APPLICATION_CREDENTIALS_JSON')

if not encoded_credentials:
    print("ERROR: The GOOGLE_APPLICATION_CREDENTIALS_JSON environment variable was not found.")
    print("Please ensure it is set in your .env file and that you are running this from the project root.")
else:
    print(f"SUCCESS: Found the environment variable.")
    print(f"Raw string length: {len(encoded_credentials)} characters.")
    print(f"Raw string (first 100 chars): {encoded_credentials[:100]}")
    print("-" * 50)
    
    try:
        # Step 1: Base64 Decode
        decoded_bytes = base64.b64decode(encoded_credentials)
        print("✅ Base64 decoding successful.")
        
        # Step 2: UTF-8 Decode
        json_credentials_str = decoded_bytes.decode('utf-8')
        print("✅ UTF-8 decoding successful.")
        print(f"Decoded JSON string length: {len(json_credentials_str)} characters.")
        print(f"Decoded JSON string (first 200 chars): {json_credentials_str[:200]}")
        print("-" * 50)
        
        # Step 3: JSON Parse
        service_account_dict = json.loads(json_credentials_str)
        print("✅ JSON parsing successful!")
        print("🎉 Your credentials are correct and can be parsed.")
        print(f"Project ID from credentials: {service_account_dict.get('project_id')}")
        
    except Exception as e:
        print(f"❌ AN ERROR OCCURRED: {e}")
        print("This is the exact error your application is seeing.")
        print("The problem is either in the .env file itself or how the variable is being read.")

print("--- Diagnostic Complete ---")