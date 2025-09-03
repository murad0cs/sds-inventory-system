#!/usr/bin/env python3
import requests
import json
import time

BASE_URL = "http://localhost:8000/api/v1"

def test_api():
    print("\n=== Testing SDS Chemical Inventory API ===\n")
    
    # Test 1: Create a chemical
    print("1. Creating a new chemical...")
    chemical_data = {
        "name": "Ethanol",
        "cas_number": "64-17-5",
        "quantity": 500.0,
        "unit": "ml"
    }
    response = requests.post(f"{BASE_URL}/chemicals/", json=chemical_data)
    if response.status_code == 200:
        created_chemical = response.json()
        chemical_id = created_chemical["id"]
        print(f"   ✅ Chemical created with ID: {chemical_id}")
    else:
        print(f"   ❌ Failed to create chemical: {response.text}")
        return
    
    # Test 2: Get all chemicals
    print("\n2. Getting all chemicals...")
    response = requests.get(f"{BASE_URL}/chemicals/")
    if response.status_code == 200:
        chemicals = response.json()
        print(f"   ✅ Found {len(chemicals)} chemical(s)")
    else:
        print(f"   ❌ Failed to get chemicals: {response.text}")
    
    # Test 3: Get specific chemical (using asyncpg)
    print(f"\n3. Getting chemical by ID (using asyncpg)...")
    response = requests.get(f"{BASE_URL}/chemicals/{chemical_id}")
    if response.status_code == 200:
        print(f"   ✅ Retrieved chemical: {response.json()['name']}")
    else:
        print(f"   ❌ Failed to get chemical: {response.text}")
    
    # Test 4: Update chemical
    print(f"\n4. Updating chemical...")
    update_data = {"quantity": 750.0}
    response = requests.put(f"{BASE_URL}/chemicals/{chemical_id}", json=update_data)
    if response.status_code == 200:
        updated = response.json()
        print(f"   ✅ Updated quantity to: {updated['quantity']}")
    else:
        print(f"   ❌ Failed to update chemical: {response.text}")
    
    # Test 5: Create inventory log
    print(f"\n5. Creating inventory log...")
    log_data = {
        "action_type": "add",
        "quantity": 250.0
    }
    response = requests.post(f"{BASE_URL}/chemicals/{chemical_id}/log", json=log_data)
    if response.status_code == 200:
        print(f"   ✅ Log entry created")
    else:
        print(f"   ❌ Failed to create log: {response.text}")
    
    # Test 6: Get inventory logs (using asyncpg)
    print(f"\n6. Getting inventory logs (using asyncpg)...")
    response = requests.get(f"{BASE_URL}/chemicals/{chemical_id}/logs")
    if response.status_code == 200:
        logs = response.json()
        print(f"   ✅ Found {len(logs)} log entry(ies)")
    else:
        print(f"   ❌ Failed to get logs: {response.text}")
    
    # Test 7: Create another chemical
    print("\n7. Creating another chemical...")
    chemical_data_2 = {
        "name": "Acetone",
        "cas_number": "67-64-1",
        "quantity": 1000.0,
        "unit": "ml"
    }
    response = requests.post(f"{BASE_URL}/chemicals/", json=chemical_data_2)
    if response.status_code == 200:
        print(f"   ✅ Second chemical created")
    else:
        print(f"   ❌ Failed to create second chemical: {response.text}")
    
    # Test 8: Delete first chemical
    print(f"\n8. Deleting chemical...")
    response = requests.delete(f"{BASE_URL}/chemicals/{chemical_id}")
    if response.status_code == 204:
        print(f"   ✅ Chemical deleted successfully")
    else:
        print(f"   ❌ Failed to delete chemical: {response.text}")
    
    print("\n=== All tests completed! ===\n")

if __name__ == "__main__":
    # Wait a moment for the API to be ready
    max_attempts = 10
    for i in range(max_attempts):
        try:
            response = requests.get("http://localhost:8000/health")
            if response.status_code == 200:
                test_api()
                break
        except:
            if i == max_attempts - 1:
                print("API is not available. Please ensure it's running.")
            else:
                print(f"Waiting for API to be ready... ({i+1}/{max_attempts})")
                time.sleep(2)