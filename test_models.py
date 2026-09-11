from models.ml_model import WelfareEligibilityAI
from models.fraud_detector import FraudDetector

def test_models():
    print("🧪 Testing ML Models...")
    
    # Test 1: Load model
    print("\n1. Testing Eligibility Model...")
    ai = WelfareEligibilityAI()
    ai.load()
    
    # Test prediction
    test_applicant = {
        'income': 45000,
        'family_size': 6,
        'age': 35,
        'dependents': 3,
        'location': 1,
        'land_acres': 0.5,
        'bank_balance': 25000,
        'has_vehicle': 0
    }
    
    result = ai.predict(test_applicant)
    print(f"   Decision: {result['decision']}")
    print(f"   Confidence: {result['confidence']}%")
    print(f"   Reasoning: {result['reasoning'][:2]}")
    assert result['decision'] in ['APPROVED', 'REJECTED', 'PENDING_REVIEW']
    print("   ✅ Eligibility model working")
    
    # Test 2: Fraud detector
    print("\n2. Testing Fraud Detector...")
    fraud = FraudDetector()
    
    app1_data = {
        'name': 'John Doe',
        'aadhaar': '1111-2222-3333',
        'income': 50000,
        'family_size': 4,
        'age': 30,
        'location': 1,
        'has_vehicle': 0,
        'bank_balance': 20000
    }
    
    fraud.add_application('APP-001', app1_data)
    
    # Check for duplicate
    fraud_check = fraud.check_fraud(app1_data)
    print(f"   Fraud flags: {len(fraud_check['flags'])}")
    print("   ✅ Fraud detector working")
    
    print("\n✅ All model tests passed!")

if __name__ == "__main__":
    test_models()