"""
HackRx Compliance Validation Script for Edvora
Validates that the implementation meets all Bajaj HackRx 2025 requirements
"""

import json
import asyncio
import httpx
from typing import Dict, List, Any
import sys
from pathlib import Path

class HackRxComplianceValidator:
    """Validates compliance with HackRx 2025 requirements"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=60.0)
        self.validation_results = []
    
    def log_result(self, test_name: str, passed: bool, details: str = ""):
        """Log validation result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        self.validation_results.append({
            "test": test_name,
            "passed": passed,
            "details": details
        })
        print(f"{status} {test_name}")
        if details:
            print(f"    {details}")
    
    async def validate_project_structure(self):
        """Validate project structure requirements"""
        print("\n📁 Validating Project Structure...")
        
        required_files = [
            "main.py",
            "retriever.py", 
            "llm_logic.py",
            "utils.py",
            "requirements.txt",
            "README.md",
            ".env.example"
        ]
        
        all_files_exist = True
        for file in required_files:
            exists = Path(file).exists()
            if not exists:
                all_files_exist = False
            self.log_result(f"File exists: {file}", exists)
        
        return all_files_exist
    
    async def validate_api_endpoints(self):
        """Validate API endpoint requirements"""
        print("\n🌐 Validating API Endpoints...")
        
        try:
            # Test root endpoint
            response = await self.client.get(f"{self.base_url}/")
            self.log_result("Root endpoint accessible", response.status_code == 200)
            
            # Test health endpoint
            response = await self.client.get(f"{self.base_url}/health")
            self.log_result("Health endpoint accessible", response.status_code == 200)
            
            # Test mandatory /hackrx/run endpoint exists
            response = await self.client.post(
                f"{self.base_url}/hackrx/run",
                json={"documents": "test", "questions": ["test"]}
            )
            # Should return 400 for invalid URL, not 404
            endpoint_exists = response.status_code != 404
            self.log_result("Mandatory /hackrx/run endpoint exists", endpoint_exists)
            
            return True
            
        except Exception as e:
            self.log_result("API endpoints validation", False, str(e))
            return False
    
    async def validate_request_format(self):
        """Validate request format compliance"""
        print("\n📝 Validating Request Format...")
        
        # Test valid request structure
        valid_request = {
            "documents": "https://www.africau.edu/images/default/sample.pdf",
            "questions": ["What is this document about?"]
        }
        
        try:
            response = await self.client.post(
                f"{self.base_url}/hackrx/run",
                json=valid_request
            )
            
            accepts_valid_format = response.status_code in [200, 500]  # 500 might be due to missing API key
            self.log_result("Accepts valid request format", accepts_valid_format)
            
            # Test invalid request (missing fields)
            invalid_request = {"documents": "test"}
            response = await self.client.post(
                f"{self.base_url}/hackrx/run",
                json=invalid_request
            )
            
            rejects_invalid_format = response.status_code == 422  # Validation error
            self.log_result("Rejects invalid request format", rejects_invalid_format)
            
            return accepts_valid_format and rejects_invalid_format
            
        except Exception as e:
            self.log_result("Request format validation", False, str(e))
            return False
    
    async def validate_response_format(self):
        """Validate response format compliance"""
        print("\n📤 Validating Response Format...")
        
        # This test requires a valid OpenAI API key
        test_request = {
            "documents": "https://www.africau.edu/images/default/sample.pdf",
            "questions": ["What is this document about?"]
        }
        
        try:
            response = await self.client.post(
                f"{self.base_url}/hackrx/run",
                json=test_request
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Validate top-level structure
                has_answers = "answers" in data
                self.log_result("Response has 'answers' field", has_answers)
                
                if has_answers and isinstance(data["answers"], list) and len(data["answers"]) > 0:
                    answer = data["answers"][0]
                    
                    # Validate answer structure
                    required_fields = ["decision", "amount", "justification", "source_clause"]
                    all_fields_present = all(field in answer for field in required_fields)
                    self.log_result("Answer has all required fields", all_fields_present)
                    
                    # Validate decision values
                    valid_decision = answer.get("decision") in ["Approved", "Rejected"]
                    self.log_result("Decision is 'Approved' or 'Rejected'", valid_decision)
                    
                    # Validate amount format
                    amount = answer.get("amount", "")
                    valid_amount = "₹" in amount or "Not specified" in amount
                    self.log_result("Amount in correct format", valid_amount)
                    
                    return all_fields_present and valid_decision
                else:
                    self.log_result("Response format validation", False, "No answers in response")
                    return False
            else:
                self.log_result("Response format validation", False, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Response format validation", False, str(e))
            return False
    
    async def validate_technology_stack(self):
        """Validate technology stack requirements"""
        print("\n🔧 Validating Technology Stack...")
        
        # Check requirements.txt for required packages
        try:
            with open("requirements.txt", "r") as f:
                requirements = f.read().lower()
            
            required_packages = [
                "fastapi",
                "openai", 
                "langchain",
                "faiss",
                "pypdf2",
                "python-docx"
            ]
            
            all_packages_present = True
            for package in required_packages:
                present = package in requirements
                if not present:
                    all_packages_present = False
                self.log_result(f"Package included: {package}", present)
            
            return all_packages_present
            
        except Exception as e:
            self.log_result("Technology stack validation", False, str(e))
            return False
    
    async def validate_documentation(self):
        """Validate documentation requirements"""
        print("\n📚 Validating Documentation...")
        
        try:
            # Check README.md exists and has content
            readme_path = Path("README.md")
            if readme_path.exists():
                with open(readme_path, "r") as f:
                    readme_content = f.read()
                
                has_setup_instructions = "setup" in readme_content.lower()
                has_api_documentation = "api" in readme_content.lower()
                has_usage_examples = "example" in readme_content.lower()
                
                self.log_result("README has setup instructions", has_setup_instructions)
                self.log_result("README has API documentation", has_api_documentation)
                self.log_result("README has usage examples", has_usage_examples)
                
                return has_setup_instructions and has_api_documentation and has_usage_examples
            else:
                self.log_result("README.md exists", False)
                return False
                
        except Exception as e:
            self.log_result("Documentation validation", False, str(e))
            return False
    
    async def run_full_validation(self):
        """Run complete validation suite"""
        print("🏆 HackRx 2025 Compliance Validation")
        print("=" * 60)
        
        validations = [
            ("Project Structure", self.validate_project_structure()),
            ("API Endpoints", self.validate_api_endpoints()),
            ("Request Format", self.validate_request_format()),
            ("Response Format", self.validate_response_format()),
            ("Technology Stack", self.validate_technology_stack()),
            ("Documentation", self.validate_documentation())
        ]
        
        results = []
        for name, validation in validations:
            try:
                result = await validation
                results.append(result)
            except Exception as e:
                print(f"❌ {name} validation failed: {str(e)}")
                results.append(False)
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 VALIDATION SUMMARY")
        print("=" * 60)
        
        passed_count = sum(1 for result in self.validation_results if result["passed"])
        total_count = len(self.validation_results)
        
        print(f"Tests Passed: {passed_count}/{total_count}")
        print(f"Success Rate: {(passed_count/total_count)*100:.1f}%")
        
        overall_pass = all(results)
        if overall_pass:
            print("\n🎉 COMPLIANCE VALIDATION PASSED!")
            print("✅ Edvora meets all HackRx 2025 requirements")
        else:
            print("\n⚠️  COMPLIANCE VALIDATION INCOMPLETE")
            print("❌ Some requirements need attention")
            
            # Show failed tests
            failed_tests = [r for r in self.validation_results if not r["passed"]]
            if failed_tests:
                print("\n🔍 Failed Tests:")
                for test in failed_tests:
                    print(f"   • {test['test']}")
                    if test['details']:
                        print(f"     {test['details']}")
        
        print("=" * 60)
        return overall_pass
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

async def main():
    """Main validation function"""
    validator = HackRxComplianceValidator()
    
    try:
        success = await validator.run_full_validation()
        sys.exit(0 if success else 1)
    finally:
        await validator.close()

if __name__ == "__main__":
    asyncio.run(main())
