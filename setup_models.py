from models.ml_model import WelfareEligibilityAI
from models.fraud_detector import FraudDetector

def setup():
    """One-time setup to train and save models"""
    print("="*50)
    print("🚀 Setting up ML models...")
    print("="*50)
    
    # Train eligibility model
    print("\n1. Training Eligibility Model...")
    ai = WelfareEligibilityAI()
    stats = ai.train(n_samples=1000)
    ai.save()
    
    print(f"\n✅ Eligibility model ready!")
    print(f"   Accuracy: {stats['test_accuracy']*100:.2f}%")
    
    # Initialize fraud detector (downloads pre-trained model)
    print("\n2. Initializing Fraud Detector...")
    fraud = FraudDetector()
    print("✅ Fraud detector ready!")
    
    print("\n" + "="*50)
    print("✅ ALL MODELS READY!")
    print("="*50)

if __name__ == "__main__":
    setup()