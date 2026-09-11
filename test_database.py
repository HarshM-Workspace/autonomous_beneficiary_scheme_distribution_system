from database import Database

def test_database():
    print("🧪 Testing Database...")
    
    db = Database('test_welfare.db')
    
    # Test 1: Create application
    test_app = {
        'app_id': 'APP-TEST-003',
        'name': 'Test User',
        'aadhaar': '1234-5678-9012',
        'income': 45000,
        'family_size': 5,
        'age': 35,
        'dependents': 3,
        'location': 1,
        'land_acres': 0.5,
        'bank_balance': 25000,
        'has_vehicle': 0,
        'ai_decision': 'APPROVED',
        'ai_confidence': 85.5,
        'ai_reasoning': ['Low income', 'Large family'],
        'fraud_flags': [],
        'status': 'PENDING_REVIEW'
    }
    
    app_id = db.add_application(test_app)
    print(f"✅ Created application: {app_id}")
    
    # Test 2: Retrieve application
    retrieved = db.get_application(app_id)
    assert retrieved['name'] == 'Test User'
    print(f"✅ Retrieved application")
    
    # Test 3: Get all applications
    all_apps = db.get_all_applications()
    assert len(all_apps) > 0
    print(f"✅ Retrieved all applications: {len(all_apps)}")
    
    # Test 4: Update review
    db.update_application_review(app_id, 'OFFICER-001', 'APPROVED', 'Looks good')
    print(f"✅ Updated review")
    
    # Test 5: Get stats
    stats = db.get_stats()
    print(f"✅ Stats: {stats}")
    
    print("\n✅ All database tests passed!")

if __name__ == "__main__":
    test_database()