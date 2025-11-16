#!/usr/bin/env python
"""Fix .env file by removing null characters and ensuring proper format"""
import os
import re

print("="*60)
print("Fixing .env file")
print("="*60 + "\n")

env_file = '.env'

if not os.path.exists(env_file):
    print("❌ .env file not found")
    exit(1)

# Read the file in binary mode to detect null characters
with open(env_file, 'rb') as f:
    content = f.read()

# Check for null characters
if b'\x00' in content:
    print("⚠ Found null characters in .env file")
    # Remove null characters
    content = content.replace(b'\x00', b'')
    print("✓ Removed null characters")

# Decode to string
try:
    text = content.decode('utf-8')
except UnicodeDecodeError:
    print("⚠ Encoding issue, trying latin-1")
    text = content.decode('latin-1', errors='ignore')

# Clean up the content
lines = text.split('\n')
clean_lines = []

for line in lines:
    # Remove any remaining null characters
    line = line.replace('\x00', '')
    # Skip empty lines
    if line.strip():
        clean_lines.append(line)

# Ensure we have the required keys
has_gemini = any('GEMINI_API_KEY' in line for line in clean_lines)
has_firebase = any('GOOGLE_APPLICATION_CREDENTIALS_JSON' in line for line in clean_lines)

print(f"\nCurrent .env contents:")
for line in clean_lines:
    if '=' in line:
        key = line.split('=')[0].strip()
        # Mask sensitive values
        if 'KEY' in key or 'CREDENTIALS' in key:
            print(f"  {key}=***")
        else:
            print(f"  {line[:80]}")

# Write back clean content
with open(env_file, 'w', encoding='utf-8') as f:
    f.write('\n'.join(clean_lines))
    if not clean_lines[-1].endswith('\n'):
        f.write('\n')

print(f"\n✓ Cleaned .env file")
print(f"  - Gemini API Key: {'✓' if has_gemini else '✗'}")
print(f"  - Firebase Credentials: {'✓' if has_firebase else '✗'}")

print("\n" + "="*60)
print("✅ .env file fixed!")
print("="*60)

