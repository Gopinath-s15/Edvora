#!/usr/bin/env python3
"""
Quick test script for Hugging Face integration
"""

import os
import asyncio
import requests
from dotenv import load_dotenv

load_dotenv()

async def test_huggingface():
    """Test Hugging Face API directly"""
    hf_api_key = os.getenv("HUGGINGFACE_API_KEY")
    
    if not hf_api_key or hf_api_key == "hf_your_free_key_here":
        print("❌ Please update HUGGINGFACE_API_KEY in .env file")
        return False
    
    print(f"🧪 Testing Hugging Face with key: {hf_api_key[:10]}...")
    
    headers = {"Authorization": f"Bearer {hf_api_key}"}
    url = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium"
    
    payload = {
        "inputs": "Question: What is this document about? Answer:",
        "parameters": {"max_length": 100, "temperature": 0.1}
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        print(f"📡 Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success! Response: {result}")
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_huggingface())
