"""
Test Examples for Edvora - AI Document Reasoning System
Comprehensive tests for API compliance and functionality
"""

import asyncio
import json
import httpx
import pytest
from typing import Dict, Any

# Test configuration
BASE_URL = "http://localhost:8000"
TEST_TIMEOUT = 60

class EdvoraAPITester:
    """Test suite for Edvora API"""
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=TEST_TIMEOUT)
    
    async def test_health_check(self) -> Dict[str, Any]:
        """Test health check endpoint"""
        try:
            response = await self.client.get(f"{self.base_url}/health")
            response.raise_for_status()
            return {
                "status": "PASS",
                "response": response.json(),
                "status_code": response.status_code
            }
        except Exception as e:
            return {
                "status": "FAIL",
                "error": str(e),
                "status_code": getattr(e, 'response', {}).get('status_code', 'N/A')
            }
    
    async def test_root_endpoint(self) -> Dict[str, Any]:
        """Test root endpoint"""
        try:
            response = await self.client.get(f"{self.base_url}/")
            response.raise_for_status()
            return {
                "status": "PASS",
                "response": response.json(),
                "status_code": response.status_code
            }
        except Exception as e:
            return {
                "status": "FAIL",
                "error": str(e),
                "status_code": getattr(e, 'response', {}).get('status_code', 'N/A')
            }
    
    async def test_hackrx_endpoint(self, test_data: Dict[str, Any]) -> Dict[str, Any]:
        """Test the main /hackrx/run endpoint"""
        try:
            response = await self.client.post(
                f"{self.base_url}/hackrx/run",
                json=test_data,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            
            result = response.json()
            
            # Validate response structure
            validation_result = self.validate_response_structure(result)
            
            return {
                "status": "PASS" if validation_result["valid"] else "FAIL",
                "response": result,
                "status_code": response.status_code,
                "validation": validation_result
            }
            
        except Exception as e:
            return {
                "status": "FAIL",
                "error": str(e),
                "status_code": getattr(e, 'response', {}).get('status_code', 'N/A')
            }
    
    def validate_response_structure(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Validate response structure against HackRx specification"""
        validation_errors = []
        
        # Check top-level structure
        if "answers" not in response:
            validation_errors.append("Missing 'answers' field")
            return {"valid": False, "errors": validation_errors}
        
        if not isinstance(response["answers"], list):
            validation_errors.append("'answers' must be a list")
            return {"valid": False, "errors": validation_errors}
        
        # Check each answer structure
        required_fields = ["decision", "amount", "justification", "source_clause"]
        
        for i, answer in enumerate(response["answers"]):
            if not isinstance(answer, dict):
                validation_errors.append(f"Answer {i} must be a dictionary")
                continue
            
            for field in required_fields:
                if field not in answer:
                    validation_errors.append(f"Answer {i} missing required field: {field}")
                elif not isinstance(answer[field], str):
                    validation_errors.append(f"Answer {i} field '{field}' must be a string")
            
            # Validate decision values
            if "decision" in answer and answer["decision"] not in ["Approved", "Rejected"]:
                validation_errors.append(f"Answer {i} decision must be 'Approved' or 'Rejected'")
        
        return {
            "valid": len(validation_errors) == 0,
            "errors": validation_errors
        }
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()

# Test data examples
TEST_CASES = [
    {
        "name": "Insurance Policy Test",
        "description": "Test with insurance policy document",
        "data": {
            "documents": "https://www.africau.edu/images/default/sample.pdf",
            "questions": [
                "What is the maximum claim amount for medical expenses?",
                "Are dental treatments covered under this policy?"
            ]
        }
    },
    {
        "name": "Single Question Test",
        "description": "Test with single question",
        "data": {
            "documents": "https://www.africau.edu/images/default/sample.pdf",
            "questions": ["What are the key terms and conditions?"]
        }
    }
]

async def run_comprehensive_tests():
    """Run comprehensive test suite"""
    print("🚀 Starting Edvora API Test Suite")
    print("=" * 50)
    
    tester = EdvoraAPITester()
    
    try:
        # Test 1: Health Check
        print("\n📋 Test 1: Health Check")
        health_result = await tester.test_health_check()
        print(f"Status: {health_result['status']}")
        if health_result['status'] == 'PASS':
            print(f"Response: {json.dumps(health_result['response'], indent=2)}")
        else:
            print(f"Error: {health_result['error']}")
        
        # Test 2: Root Endpoint
        print("\n📋 Test 2: Root Endpoint")
        root_result = await tester.test_root_endpoint()
        print(f"Status: {root_result['status']}")
        if root_result['status'] == 'PASS':
            print(f"Response: {json.dumps(root_result['response'], indent=2)}")
        else:
            print(f"Error: {root_result['error']}")
        
        # Test 3: HackRx Endpoint Tests
        for i, test_case in enumerate(TEST_CASES, 1):
            print(f"\n📋 Test {i+2}: {test_case['name']}")
            print(f"Description: {test_case['description']}")
            
            hackrx_result = await tester.test_hackrx_endpoint(test_case['data'])
            print(f"Status: {hackrx_result['status']}")
            print(f"Status Code: {hackrx_result['status_code']}")
            
            if hackrx_result['status'] == 'PASS':
                print("✅ Response Structure Valid")
                print(f"Response: {json.dumps(hackrx_result['response'], indent=2)}")
            else:
                print("❌ Test Failed")
                print(f"Error: {hackrx_result.get('error', 'Unknown error')}")
                if 'validation' in hackrx_result:
                    print(f"Validation Errors: {hackrx_result['validation']['errors']}")
        
        print("\n" + "=" * 50)
        print("🎉 Test Suite Completed")
        
    except Exception as e:
        print(f"❌ Test suite failed: {str(e)}")
    
    finally:
        await tester.close()

# Manual test functions
async def test_with_custom_data():
    """Test with custom data"""
    custom_data = {
        "documents": input("Enter document URL: "),
        "questions": [input("Enter your question: ")]
    }
    
    tester = EdvoraAPITester()
    try:
        result = await tester.test_hackrx_endpoint(custom_data)
        print(f"\nResult: {json.dumps(result, indent=2)}")
    finally:
        await tester.close()

def validate_json_structure(json_data: str) -> bool:
    """Validate JSON structure for HackRx compliance"""
    try:
        data = json.loads(json_data)
        tester = EdvoraAPITester()
        validation = tester.validate_response_structure(data)
        
        print(f"Valid: {validation['valid']}")
        if not validation['valid']:
            print(f"Errors: {validation['errors']}")
        
        return validation['valid']
        
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {str(e)}")
        return False

if __name__ == "__main__":
    print("Edvora API Test Suite")
    print("Choose an option:")
    print("1. Run comprehensive tests")
    print("2. Test with custom data")
    print("3. Validate JSON structure")
    
    choice = input("Enter choice (1-3): ")
    
    if choice == "1":
        asyncio.run(run_comprehensive_tests())
    elif choice == "2":
        asyncio.run(test_with_custom_data())
    elif choice == "3":
        json_input = input("Enter JSON to validate: ")
        validate_json_structure(json_input)
    else:
        print("Invalid choice")
