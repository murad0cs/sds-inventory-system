import requests
import json
import time
import random

BASE_URL = "http://localhost:8000"

def test_api():
    print("=== Testing SDS Chemical Inventory API ===\n")
    
    # Generate unique CAS number for testing
    unique_cas = f"TEST-{int(time.time())}-{random.randint(100,999)}"
    
    # Test 1: Create Chemical
    print("1. Creating a new chemical...")
    create_data = {
        "name": "Ethanol",
        "cas_number": unique_cas,
        "quantity": 500.0,
        "unit": "ml"
    }
    response = requests.post(f"{BASE_URL}/api/v1/chemicals/", json=create_data)
    assert response.status_code == 200, f"Create failed: {response.status_code}"
    chemical = response.json()
    chemical_id = chemical["id"]
    print(f"   OK: Chemical created with ID: {chemical_id}\n")
    
    # Test 2: Get All Chemicals (with pagination)
    print("2. Getting all chemicals...")
    response = requests.get(f"{BASE_URL}/api/v1/chemicals/")
    assert response.status_code == 200, f"Get all failed: {response.status_code}"
    data = response.json()
    print(f"   OK: Found {data['total_count']} chemical(s)")
    print(f"   OK: Page {data['page']} of {data['total_pages']}\n")
    
    # Test 3: Get Chemical by ID (uses asyncpg)
    print("3. Getting chemical by ID (using asyncpg)...")
    response = requests.get(f"{BASE_URL}/api/v1/chemicals/{chemical_id}")
    assert response.status_code == 200, f"Get by ID failed: {response.status_code}"
    chemical = response.json()
    print(f"   OK: Retrieved chemical: {chemical['name']}\n")
    
    # Test 4: Update Chemical
    print("4. Updating chemical...")
    update_data = {
        "name": "Ethanol (95%)",
        "quantity": 750.0,
        "unit": "ml"
    }
    response = requests.put(f"{BASE_URL}/api/v1/chemicals/{chemical_id}", json=update_data)
    assert response.status_code == 200, f"Update failed: {response.status_code}"
    updated = response.json()
    print(f"   OK: Updated name: {updated['name']}")
    print(f"   OK: Updated quantity: {updated['quantity']} {updated['unit']}\n")
    
    # Test 5: Create Inventory Log
    print("5. Creating inventory log...")
    log_data = {
        "action_type": "add",
        "quantity": 100.0
    }
    response = requests.post(f"{BASE_URL}/api/v1/chemicals/{chemical_id}/log", json=log_data)
    assert response.status_code == 200, f"Create log failed: {response.status_code}"
    print("   OK: Inventory log created\n")
    
    # Test 6: Get Inventory Logs (uses asyncpg)
    print("6. Getting inventory logs (using asyncpg)...")
    response = requests.get(f"{BASE_URL}/api/v1/chemicals/{chemical_id}/logs")
    assert response.status_code == 200, f"Get logs failed: {response.status_code}"
    data = response.json()
    print(f"   OK: Found {data["total_count"]} log(s)\n")
    
    # Test 7: Test 404 Error
    print("7. Testing error handling (404)...")
    response = requests.get(f"{BASE_URL}/api/v1/chemicals/99999")
    assert response.status_code == 404, f"Expected 404, got: {response.status_code}"
    print("   OK: 404 error handled correctly\n")
    
    # Test 8: Delete Chemical
    print("8. Deleting chemical...")
    response = requests.delete(f"{BASE_URL}/api/v1/chemicals/{chemical_id}")
    assert response.status_code == 204, f"Delete failed: {response.status_code}"
    print("   OK: Chemical deleted\n")
    
    # Test 9: Verify Deletion
    print("9. Verifying deletion...")
    response = requests.get(f"{BASE_URL}/api/v1/chemicals/{chemical_id}")
    assert response.status_code == 404, f"Expected 404 after deletion, got: {response.status_code}"
    print("   OK: Deletion confirmed\n")
    
    print("=== All tests passed! SUCCESS: ===")

if __name__ == "__main__":
    try:
        # Check if API is running
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code != 200:
            print("ERROR: Error: API is not running. Please start it with: ./run.sh")
            exit(1)
        
        test_api()
    except requests.exceptions.ConnectionError:
        print("ERROR: Error: Cannot connect to API at http://localhost:8000")
        print("   Please ensure the API is running with: ./run.sh")
        exit(1)
    except AssertionError as e:
        print(f"\nERROR: Test failed: {e}")
        exit(1)
    except Exception as e:
        print(f"\nERROR: Unexpected error: {e}")
        exit(1)
