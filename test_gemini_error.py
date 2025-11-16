#!/usr/bin/env python
"""Test Gemini API to identify the error"""
import os
import sys

# Load .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    pass

print("="*60)
print("Testing Gemini API Configuration")
print("="*60 + "\n")

# Check API key
gemini_key = os.getenv("GEMINI_API_KEY", "AIzaSyBmzUgklO1DTbiI8IVB9XsKHJFl41RUwGU")
print(f"API Key: {gemini_key[:20]}...")
print(f"Key length: {len(gemini_key)} characters\n")

# Set environment variable
os.environ["GEMINI_API_KEY"] = gemini_key

# Test with litellm directly
try:
    import litellm
    
    print("Testing with litellm...\n")
    
    # Try different model name formats
    models_to_try = [
        "gemini-2.5-flash",
        "gemini/gemini-2.5-flash",
        "gemini/gemini-2.0-flash-exp",
        "gemini/gemini-1.5-flash"
    ]
    
    for model_name in models_to_try:
        print(f"Trying model: {model_name}")
        try:
            response = litellm.completion(
                model=model_name,
                messages=[{"role": "user", "content": "Say hello in Arabic"}],
                api_key=gemini_key
            )
            if response and response.choices and response.choices[0].message.content:
                print(f"  ✅ SUCCESS! Model works: {model_name}")
                print(f"  Response: {response.choices[0].message.content[:100]}")
                print(f"\n✅ Use this model name: {model_name}")
                break
            else:
                print(f"  ✗ Empty or invalid response")
        except Exception as e:
            error_msg = str(e)
            print(f"  ✗ Error: {error_msg[:200]}")
            if "model" in error_msg.lower() or "not found" in error_msg.lower() or "invalid" in error_msg.lower():
                print(f"     → Model name might be incorrect")
            elif "api" in error_msg.lower() or "key" in error_msg.lower() or "auth" in error_msg.lower():
                print(f"     → API key might be invalid")
            elif "rate limit" in error_msg.lower():
                print(f"     → Rate limit exceeded")
    
    print("\n" + "="*60)
    
except ImportError:
    print("❌ litellm not available")
    print("Install with: pip install litellm")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)

