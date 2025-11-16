#!/usr/bin/env python
"""Fix .env file and ensure Gemini API key is set"""
import os

print("="*60)
print("Fixing .env file")
print("="*60 + "\n")

env_file = '.env'
gemini_key = "AIzaSyBmzUgklO1DTbiI8IVB9XsKHJFl41RUwGU"

# Read existing .env if it exists
env_vars = {}
if os.path.exists(env_file):
    try:
        with open(env_file, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                # Skip comments and empty lines
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    # Remove any null characters
                    value = value.strip().replace('\x00', '')
                    if key:
                        env_vars[key] = value
        print(f"✓ Read existing .env file")
    except Exception as e:
        print(f"⚠ Error reading .env: {e}")
        print("  Creating new .env file")

# Update/Add Gemini API key
env_vars['GEMINI_API_KEY'] = gemini_key
print(f"✓ Set GEMINI_API_KEY")

# Write clean .env file
with open(env_file, 'w', encoding='utf-8') as f:
    for key, value in env_vars.items():
        # Ensure no null characters
        clean_value = value.replace('\x00', '').replace('\n', '')
        f.write(f"{key}={clean_value}\n")

print(f"✓ Wrote clean .env file")
print(f"\nEnvironment variables:")
for key in sorted(env_vars.keys()):
    if 'KEY' in key or 'CREDENTIALS' in key:
        print(f"  {key}=***")
    else:
        print(f"  {key}={env_vars[key]}")

print("\n" + "="*60)
print("✅ .env file fixed and Gemini API key configured!")
print("="*60)

