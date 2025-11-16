#!/usr/bin/env python
"""Quick test using the Firebase tool directly"""
import os
import sys

# Load .env
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

sys.path.insert(0, 'src')

print("Testing Firebase Products Read...")
print("="*50)

try:
    from trent_agent.tools.firebase_tool import FirebaseReadOnlyTool
    
    tool = FirebaseReadOnlyTool()
    print("✓ Tool initialized\n")
    
    print("Querying products (limit 5 for quick test)...")
    # Query with a limit by getting first 5
    result = tool._run(
        operation="query",
        collection="products",
        return_objects=True
    )
    
    print("✓ Query completed\n")
    print("Result preview:")
    print("-" * 50)
    print(str(result)[:500])
    print("-" * 50)
    
    # Try to parse JSON
    import json
    try:
        data = json.loads(result) if isinstance(result, str) else result
        if isinstance(data, dict):
            total = data.get('total', 0)
            print(f"\nTotal products: {total}")
            if total > 0:
                docs = data.get('documents', [])
                print(f"Sample products: {len(docs[:3])} shown")
                for i, doc in enumerate(docs[:3], 1):
                    print(f"  {i}. Title: {doc.get('title', 'N/A')}, CategoryId: {doc.get('categoryId', 'N/A')}")
    except:
        pass
    
    print("\n✅ Test completed!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

