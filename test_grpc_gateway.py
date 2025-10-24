#!/usr/bin/env python3
"""
Test script for gRPC HTTP Gateway
"""

import requests
import json
import time

BASE_URL = "http://localhost:8080"

def test_health():
    """Test health endpoint"""
    print("🔍 Testing Health Check...")
    response = requests.get(f"{BASE_URL}/api/v1/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_status():
    """Test server status"""
    print("🔍 Testing Server Status...")
    response = requests.get(f"{BASE_URL}/api/v1/status")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_execute_code():
    """Test code execution"""
    print("🔍 Testing Code Execution...")
    
    payload = {
        "language": 1,  # Python
        "code": "def add(a, b):\n    return a + b",
        "function_name": "add",
        "test_cases": [
            {
                "input_json": '{"a": 5, "b": 3}',
                "expected_output": "8",
                "timeout_ms": 1000
            },
            {
                "input_json": '{"a": 10, "b": 20}',
                "expected_output": "30",
                "timeout_ms": 1000
            }
        ]
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/executor/execute",
        json=payload
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_validate_syntax():
    """Test syntax validation"""
    print("🔍 Testing Syntax Validation...")
    
    payload = {
        "language": 1,  # Python
        "code": "def hello():\n    print('Hello, World!')"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/executor/validate",
        json=payload
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_root():
    """Test root endpoint"""
    print("🔍 Testing Root Endpoint (API Documentation)...")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Available Endpoints:")
    data = response.json()
    for category, endpoints in data.get("endpoints", {}).items():
        print(f"\n  📁 {category.upper()}:")
        for endpoint, description in endpoints.items():
            print(f"    • {endpoint}: {description}")
    print()

def main():
    """Run all tests"""
    print("=" * 70)
    print("🧪 gRPC HTTP Gateway - Test Suite")
    print("=" * 70)
    print()
    
    # Wait a moment for services to be ready
    print("⏳ Waiting for services to be ready...")
    time.sleep(2)
    
    try:
        # Test root endpoint
        test_root()
        
        # Test health check
        test_health()
        
        # Test server status
        test_status()
        
        # Test syntax validation
        test_validate_syntax()
        
        # Test code execution
        test_execute_code()
        
        print("=" * 70)
        print("✅ All tests completed!")
        print("=" * 70)
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the gateway.")
        print("   Make sure the gRPC services and gateway are running:")
        print("   python start_grpc_services.py")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()

