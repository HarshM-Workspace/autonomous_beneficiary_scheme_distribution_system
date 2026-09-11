import requests
import time

BASE_URL = 'http://localhost:5000'

def test_complete_workflow():
    print("🧪 Testing Complete Workflow...")
    
    # Step 1: Submit Application
    print("\n1. Submitting application...")
    app_data = {
        'name': 'Integration Test User',
        'aadhaar': '1111-2222-9999',
        'income': '45000',
        'family_size': '6',
        'age': '35',
        'dependents': '3',
        'location': '1',
        'land_acres': '0.5',
        'bank_balance': '25000',
        'has_vehicle': '0'
    }
    
    response = requests.post(f'{BASE_URL}/apply', data=app_data)
    assert response.status_code == 200
    print("   ✅ Application submitted")
    
    # Step 2: Check Dashboard
    print("\n2. Checking dashboard...")
    response = requests.get(f'{BASE_URL}/dashboard')
    assert response.status_code == 200
    assert 'Integration Test User' in response.text
    print("   ✅ Application appears in dashboard")
    
    # Step 3: Check Stats API
    print("\n3. Checking stats...")
    response = requests.get(f'{BASE_URL}/api/stats')
    data = response.json()
    assert data['applications']['total'] > 0
    print(f"   Total applications: {data['applications']['total']}")
    print("   ✅ Stats working")
    
    # Step 4: Check Blockchain
    print("\n4. Checking blockchain...")
    response = requests.get(f'{BASE_URL}/blockchain-view')
    assert response.status_code == 200
    print("   ✅ Blockchain accessible")
    
    print("\n✅ Complete workflow test passed!")

if __name__ == "__main__":
    print("⚠ Make sure Flask app is running")
    input("Press Enter to start integration test...")
    test_complete_workflow()