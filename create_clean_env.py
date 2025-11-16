#!/usr/bin/env python
"""Create a clean .env file"""
import os

# Read existing Firebase credentials if they exist
firebase_creds = None
if os.path.exists('.env'):
    try:
        with open('.env', 'rb') as f:
            content = f.read().replace(b'\x00', b'').decode('utf-8', errors='ignore')
            for line in content.split('\n'):
                if 'GOOGLE_APPLICATION_CREDENTIALS_JSON' in line and '=' in line:
                    firebase_creds = line.split('=', 1)[1].strip()
                    break
    except:
        pass

# Create clean .env file
with open('.env', 'w', encoding='utf-8') as f:
    f.write('GEMINI_API_KEY=AIzaSyBmzUgklO1DTbiI8IVB9XsKHJFl41RUwGU\n')
    if firebase_creds:
        f.write(f'GOOGLE_APPLICATION_CREDENTIALS_JSON={firebase_creds}\n')

print("✅ Created clean .env file with Gemini API key")
if firebase_creds:
    print("✅ Preserved Firebase credentials")

