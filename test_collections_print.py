#!/usr/bin/env python
"""Test that collections are printed when Firebase tool initializes"""
import os
import sys

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

print("Testing Firebase Tool Initialization...")
print("(This should print all collections)\n")

try:
    from src.trent_agent.tools.firebase_tool import FirebaseReadOnlyTool
    
    print("Initializing FirebaseReadOnlyTool...")
    tool = FirebaseReadOnlyTool()
    print("\n✓ Tool initialized successfully!")
    print("Collections should have been printed above.")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

