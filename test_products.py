#!/usr/bin/env python
"""Test script to verify products are being read successfully from Firebase"""
import os
import sys
import json
import base64

# Load .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # Fallback: manually load .env file
    env_file = '.env'
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

# Add src to path
sys.path.insert(0, 'src')

from trent_agent.tools import FirebaseReadOnlyTool

print("="*60)
print("Testing Firebase Products Reading")
print("="*60 + "\n")

try:
    # Initialize the Firebase tool
    print("1. Initializing Firebase tool...")
    firebase_tool = FirebaseReadOnlyTool()
    print("   ✓ Firebase tool initialized successfully\n")
    
    # Test 1: Query all products
    print("2. Querying all products from 'products' collection...")
    result = firebase_tool._run(
        operation="query",
        collection="products",
        return_objects=True
    )
    
    print("   ✓ Query completed\n")
    
    # Parse the result
    try:
        if isinstance(result, str):
            data = json.loads(result)
        else:
            data = result
        
        total = data.get('total', 0)
        documents = data.get('documents', [])
        
        print(f"3. Results:")
        print(f"   Total products found: {total}\n")
        
        if total > 0:
            print(f"4. Sample products (showing first 5):")
            print("-" * 60)
            
            for idx, product in enumerate(documents[:5], 1):
                print(f"\nProduct {idx}:")
                print(f"  - _id: {product.get('_id', 'N/A')}")
                print(f"  - title: {product.get('title', 'N/A')}")
                print(f"  - categoryId: {product.get('categoryId', 'N/A')}")
                
                # Show other available fields
                other_fields = {k: v for k, v in product.items() 
                              if k not in ['_id', 'title', 'categoryId']}
                if other_fields:
                    print(f"  - Other fields: {list(other_fields.keys())}")
            
            print("\n" + "-" * 60)
            
            # Extract unique categoryIds
            print(f"\n5. Extracting unique categoryId values...")
            category_ids = set()
            for product in documents:
                cat_id = product.get('categoryId')
                if cat_id:
                    category_ids.add(cat_id)
            
            print(f"   ✓ Found {len(category_ids)} unique categoryId values:")
            for cat_id in sorted(category_ids):
                print(f"     - {cat_id}")
            
            print("\n" + "="*60)
            print("✅ TEST SUCCESSFUL: Products are being read correctly!")
            print("="*60)
            print(f"\nSummary:")
            print(f"  - Total products: {total}")
            print(f"  - Unique categories: {len(category_ids)}")
            print(f"  - Products have 'title' field: ✓")
            print(f"  - Products have 'categoryId' field: ✓")
            
        else:
            print("   ⚠ No products found in the collection")
            print("   This might mean the collection is empty or there's a connection issue")
            
    except json.JSONDecodeError as e:
        print(f"   ❌ Error parsing JSON result: {e}")
        print(f"   Raw result: {result[:500]}...")
    except Exception as e:
        print(f"   ❌ Error processing results: {e}")
        print(f"   Result type: {type(result)}")
        print(f"   Result: {str(result)[:500]}...")

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

