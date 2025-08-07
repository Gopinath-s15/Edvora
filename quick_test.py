#!/usr/bin/env python3
"""
Quick test of the deployed HackRx API
"""

import requests
import json
import time

def test_api():
    url = "https://edvora-api.onrender.com/hackrx/run"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer hackrx_test_token"
    }
    
    # Test with a simple question that should trigger fallback
    data = {
        "documents": "https://example.com/test.pdf",
        "questions": ["What is the grace period for premium payment?"]
    }
    
    print("🧪 Testing HackRx API...")
    print(f"📡 URL: {url}")
    
    start_time = time.time()
    
    try:
        response = requests.post(url, json=data, headers=headers, timeout=30)
        end_time = time.time()
        
        print(f"⏱️  Response Time: {end_time - start_time:.2f}s")
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Success!")
            print(f"📋 Response: {json.dumps(result, indent=2)}")
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

if __name__ == "__main__":
    success = test_api()
    if success:
        print("\n🎉 API is working! Ready for HackRx submission!")
    else:
        print("\n⚠️  API needs fixing before submission")
