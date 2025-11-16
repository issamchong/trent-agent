#!/usr/bin/env python
"""Update .env file with Gemini API key"""
import os

gemini_api_key = "AIzaSyBmzUgklO1DTbiI8IVB9XsKHJFl41RUwGU"

print("="*60)
print("Updating .env file with Gemini API Key")
print("="*60 + "\n")

env_file = '.env'
env_lines = []

# Read existing .env file
if os.path.exists(env_file):
    with open(env_file, 'r', encoding='utf-8') as f:
        env_lines = f.readlines()
    print(f"✓ Read existing .env file ({len(env_lines)} lines)")
else:
    print("⚠ .env file not found, will create new one")

# Update or add GEMINI_API_KEY
updated = False
new_env_lines = []

for line in env_lines:
    stripped = line.strip()
    # Remove old OPENAI_API_KEY if exists
    if stripped.startswith('OPENAI_API_KEY='):
        print("  Removing old OPENAI_API_KEY")
        continue
    # Update or add GEMINI_API_KEY
    if stripped.startswith('GEMINI_API_KEY='):
        new_env_lines.append(f'GEMINI_API_KEY={gemini_api_key}\n')
        updated = True
        print("  ✓ Updated existing GEMINI_API_KEY")
    else:
        new_env_lines.append(line)

if not updated:
    # Add new line if it doesn't exist
    if new_env_lines and not new_env_lines[-1].endswith('\n'):
        new_env_lines.append('\n')
    new_env_lines.append(f'GEMINI_API_KEY={gemini_api_key}\n')
    print("  ✓ Added new GEMINI_API_KEY")

# Write back to .env file
with open(env_file, 'w', encoding='utf-8') as f:
    f.writelines(new_env_lines)

print(f"✓ Updated .env file successfully")
print(f"\n✓ Gemini API Key: {gemini_api_key[:20]}...")
print("\n" + "="*60)
print("✅ Gemini API Key configured!")
print("="*60)
print("\nNext: Update agents.yaml to use Gemini model")

