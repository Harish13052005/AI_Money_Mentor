import sys
import requests
import json
from dotenv import load_dotenv
import os
import pytest

load_dotenv()

# Test configuration
BASE_URL = "http://localhost:8000"
SAMPLE_DATA = {
    "income": 5000,
    "expenses": 3000,
    "savings": 1000,
    "investments": [
        {"type": "stocks", "amount": 2000},
        {"type": "mutual_funds", "amount": 1000}
    ],
    "goals": ["buy house", "retirement", "early education funding"]
}

def test_analyze_endpoint():
    """Runs a real HTTP request to the /analyze endpoint and returns the result for fixtures/tests."""

    print("\n" + "="*60)
    print("Testing /analyze endpoint")
    print("="*60)
    
    try:
        response = requests.post(f"{BASE_URL}/analyze", json=SAMPLE_DATA, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("\n✓ Analysis successful!")
            print(f"  Summary: {result['summary']}")
            print(f"  Risk Level: {result['risk_level']}")
            print(f"  Issues Found: {len(result['issues'])}")
            for issue in result['issues'][:3]:
                print(f"    - {issue}")
            return result
        else:
            print(f"✗ Error: {response.json()}")
            return None
    except Exception as e:
        print(f"✗ Connection Error: {str(e)}")
        print(f"  Make sure the server is running at {BASE_URL}")
        return None

@pytest.fixture(scope='module')
def analysis():
    return test_analyze_endpoint()


def test_explain_endpoint(analysis):
    if not analysis:
        return
    
    print("\n" + "="*60)
    print("Testing /explain endpoint")
    print("="*60)
    
    question = "Based on my current savings rate, should I increase my investment contributions?"
    
    try:
        params = {"question": question, "context": ""}
        response = requests.post(f"{BASE_URL}/explain", params=params, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("\n✓ Explanation generated!")
            print(f"  Q: {question}")
            print(f"  A: {result['explanation'][:200]}...")
        else:
            print(f"✗ Error: {response.json()}")
    except Exception as e:
        print(f"✗ Connection Error: {str(e)}")

def check_setup():
    print("\n" + "="*60)
    print("System Configuration Check")
    print("="*60)
    
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key and api_key != "your-openai-api-key-here":
        print("✓ OpenAI API Key: Configured")
    else:
        print("✗ OpenAI API Key: NOT SET")
        print("  Please set OPENAI_API_KEY in the .env file")
    
    print(f"✓ Python Version: {sys.version.split()[0]}")

if __name__ == "__main__":
    check_setup()
    
    print("\n" + "="*60)
    print("Running API Tests")
    print("="*60)
    
    result = test_analyze_endpoint()
    test_explain_endpoint(result)