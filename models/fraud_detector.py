from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class FraudDetector:
    def __init__(self):
        print("Loading fraud detection model...")
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.application_database = []
        print("✅ Fraud detection model loaded")
    
    def create_application_text(self, app_data):
        """Convert application to text for embedding"""
        text = f"""
        Name: {app_data['name']}
        Aadhaar: {app_data['aadhaar']}
        Income: {app_data['income']}
        Family: {app_data['family_size']}
        Age: {app_data['age']}
        Location: {app_data['location']}
        """
        return text.strip()
    
    def add_application(self, app_id, app_data):
        """Add application to fraud detection database"""
        app_text = self.create_application_text(app_data)
        embedding = self.model.encode(app_text)
        
        self.application_database.append({
            'id': app_id,
            'text': app_text,
            'embedding': embedding,
            'aadhaar': app_data['aadhaar']
        })
    
    def check_fraud(self, new_app_data, threshold=0.85):
        """Check if application is potentially fraudulent"""
        flags = []
        similar_apps = []
        
        # Check 1: Duplicate Aadhaar
        for app in self.application_database:
            if app['aadhaar'] == new_app_data['aadhaar']:
                flags.append(f"🚨 CRITICAL: Duplicate Aadhaar number found (App: {app['id']})")
        
        # Check 2: Similar applications (text similarity)
        if len(self.application_database) > 0:
            new_text = self.create_application_text(new_app_data)
            new_embedding = self.model.encode(new_text)
            
            for app in self.application_database:
                similarity = cosine_similarity(
                    [new_embedding],
                    [app['embedding']]
                )[0][0]
                
                if similarity > threshold:
                    similar_apps.append({
                        'app_id': app['id'],
                        'similarity': round(float(similarity * 100), 2)
                    })
                    flags.append(
                        f"⚠ Highly similar to application {app['id']} "
                        f"({similarity*100:.1f}% match)"
                    )
        
        # Check 3: Income-asset mismatch
        if new_app_data['has_vehicle'] and new_app_data['income'] < 50000:
            flags.append("⚠ Income-asset mismatch: Low income but owns vehicle")
        
        if new_app_data['bank_balance'] > 500000 and new_app_data['income'] < 100000:
            flags.append("⚠ High bank balance relative to declared income")
        
        is_fraud = len(flags) > 0
        fraud_confidence = max([s['similarity'] for s in similar_apps]) if similar_apps else 0
        
        return {
            'is_fraud': is_fraud,
            'fraud_confidence': fraud_confidence,
            'flags': flags,
            'similar_applications': similar_apps
        }