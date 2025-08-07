#!/usr/bin/env python3
"""
Official HackRx 6.0 API Testing Script
Tests the /hackrx/run endpoint with official competition examples
"""

import asyncio
import json
import httpx
from typing import Dict, Any

# Official HackRx 6.0 test data
HACKRX_TEST_DATA = {
    "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
    "questions": [
        "What is the grace period for premium payment under the National Parivar Mediclaim Plus Policy?",
        "What is the waiting period for pre-existing diseases (PED) to be covered?",
        "Does this policy cover maternity expenses, and what are the conditions?",
        "What is the waiting period for cataract surgery?",
        "Are the medical expenses for an organ donor covered under this policy?",
        "What is the No Claim Discount (NCD) offered in this policy?",
        "Is there a benefit for preventive health check-ups?",
        "How does the policy define a 'Hospital'?",
        "What is the extent of coverage for AYUSH treatments?",
        "Are there any sub-limits on room rent and ICU charges for Plan A?"
    ]
}

# Expected responses from HackRx documentation
EXPECTED_RESPONSES = [
    "A grace period of thirty days is provided for premium payment after the due date to renew or continue the policy without losing continuity benefits.",
    "There is a waiting period of thirty-six (36) months of continuous coverage from the first policy inception for pre-existing diseases and their direct complications to be covered.",
    "Yes, the policy covers maternity expenses, including childbirth and lawful medical termination of pregnancy. To be eligible, the female insured person must have been continuously covered for at least 24 months. The benefit is limited to two deliveries or terminations during the policy period.",
    "The policy has a specific waiting period of two (2) years for cataract surgery.",
    "Yes, the policy indemnifies the medical expenses for the organ donor's hospitalization for the purpose of harvesting the organ, provided the organ is for an insured person and the donation complies with the Transplantation of Human Organs Act, 1994.",
    "A No Claim Discount of 5% on the base premium is offered on renewal for a one-year policy term if no claims were made in the preceding year. The maximum aggregate NCD is capped at 5% of the total base premium.",
    "Yes, the policy reimburses expenses for health check-ups at the end of every block of two continuous policy years, provided the policy has been renewed without a break. The amount is subject to the limits specified in the Table of Benefits.",
    "A hospital is defined as an institution with at least 10 inpatient beds (in towns with a population below ten lakhs) or 15 beds (in all other places), with qualified nursing staff and medical practitioners available 24/7, a fully equipped operation theatre, and which maintains daily records of patients.",
    "The policy covers medical expenses for inpatient treatment under Ayurveda, Yoga, Naturopathy, Unani, Siddha, and Homeopathy systems up to the Sum Insured limit, provided the treatment is taken in an AYUSH Hospital.",
    "Yes, for Plan A, the daily room rent is capped at 1% of the Sum Insured, and ICU charges are capped at 2% of the Sum Insured. These limits do not apply if the treatment is for a listed procedure in a Preferred Provider Network (PPN)."
]

async def test_local_api():
    """Test the local API with HackRx official examples"""
    url = "http://localhost:8000/hackrx/run"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer hackrx_test_token_2025"
    }
    
    print("🧪 Testing Local HackRx 6.0 API")
    print("=" * 50)
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(url, json=HACKRX_TEST_DATA, headers=headers)
            
            print(f"📡 Status Code: {response.status_code}")
            print(f"⏱️  Response Time: {response.elapsed.total_seconds():.2f}s")
            
            if response.status_code == 200:
                result = response.json()
                answers = result.get("answers", [])
                
                print(f"✅ Success! Received {len(answers)} answers")
                print("\n📋 Results:")
                
                for i, (question, answer) in enumerate(zip(HACKRX_TEST_DATA["questions"], answers), 1):
                    print(f"\n{i}. Q: {question}")
                    print(f"   A: {answer}")
                    
                    # Compare with expected response
                    if i <= len(EXPECTED_RESPONSES):
                        expected = EXPECTED_RESPONSES[i-1]
                        similarity = calculate_similarity(answer, expected)
                        print(f"   📊 Similarity to expected: {similarity:.1f}%")
                
                return True
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Exception: {e}")
            return False

async def test_deployed_api():
    """Test the deployed API on Render"""
    url = "https://edvora-api.onrender.com/hackrx/run"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer hackrx_test_token_2025"
    }
    
    print("\n🚀 Testing Deployed HackRx 6.0 API")
    print("=" * 50)
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(url, json=HACKRX_TEST_DATA, headers=headers)
            
            print(f"📡 Status Code: {response.status_code}")
            print(f"⏱️  Response Time: {response.elapsed.total_seconds():.2f}s")
            
            if response.status_code == 200:
                result = response.json()
                answers = result.get("answers", [])
                
                print(f"✅ Success! Received {len(answers)} answers")
                print(f"🎯 Ready for HackRx submission!")
                
                return True
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Exception: {e}")
            return False

def calculate_similarity(text1: str, text2: str) -> float:
    """Simple similarity calculation"""
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    if not words1 and not words2:
        return 100.0
    if not words1 or not words2:
        return 0.0
    
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    
    return (len(intersection) / len(union)) * 100

async def main():
    """Run all tests"""
    print("🏆 HackRx 6.0 - Official API Testing")
    print("🎯 Bajaj Finserv Competition")
    print("=" * 60)
    
    # Test local API first
    local_success = await test_local_api()
    
    # Test deployed API
    deployed_success = await test_deployed_api()
    
    print("\n" + "=" * 60)
    print("📊 Test Summary:")
    print(f"   Local API: {'✅ PASS' if local_success else '❌ FAIL'}")
    print(f"   Deployed API: {'✅ PASS' if deployed_success else '❌ FAIL'}")
    
    if deployed_success:
        print("\n🎉 Your API is ready for HackRx 6.0 submission!")
        print("🔗 Submission URL: https://edvora-api.onrender.com/hackrx/run")
    else:
        print("\n⚠️  Please fix issues before submitting to HackRx")

if __name__ == "__main__":
    asyncio.run(main())
