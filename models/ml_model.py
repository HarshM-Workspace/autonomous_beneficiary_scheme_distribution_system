 
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import joblib
import os

class WelfareEligibilityAI:
    def __init__(self):
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            n_jobs=-1,
            random_state=42
        )
        self.scaler = StandardScaler()
        self.feature_names = [
            'income', 'family_size', 'age', 'dependents',
            'location', 'land_acres', 'bank_balance', 'has_vehicle'
        ]
        self.trained = False
    
    def generate_synthetic_data(self, n_samples=1000):
        """Generate synthetic training data"""
        np.random.seed(42)
        
        data = {
            'income': np.random.randint(10000, 500000, n_samples),
            'family_size': np.random.randint(1, 10, n_samples),
            'age': np.random.randint(18, 80, n_samples),
            'dependents': np.random.randint(0, 7, n_samples),
            'location': np.random.choice([0, 1, 2], n_samples),
            'land_acres': np.random.uniform(0, 10, n_samples),
            'bank_balance': np.random.randint(0, 1000000, n_samples),
            'has_vehicle': np.random.choice([0, 1], n_samples),
        }
        
        df = pd.DataFrame(data)
        
        # Generate labels with realistic logic
        labels = []
        for _, row in df.iterrows():
            score = 0
            
            # Positive factors
            if row['income'] < 100000: score += 40
            if row['family_size'] > 4: score += 15
            if row['dependents'] > 2: score += 15
            if row['location'] > 0: score += 10  # rural/tribal priority
            if row['age'] > 60 or row['age'] < 25: score += 10
            if row['land_acres'] < 2: score += 10
            
            # Negative factors
            if row['bank_balance'] > 500000: score -= 30
            if row['has_vehicle'] and row['income'] < 50000: score -= 20
            
            labels.append(1 if score >= 50 else 0)
        
        return df, np.array(labels)
    
    def train(self, n_samples=1000):
        """Train the model"""
        from sklearn.model_selection import train_test_split
        
        print(f"Generating {n_samples} training samples...")
        X, y = self.generate_synthetic_data(n_samples)
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        print("Scaling features...")
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        print("Training model...")
        self.model.fit(X_train_scaled, y_train)
        
        train_acc = self.model.score(X_train_scaled, y_train)
        test_acc = self.model.score(X_test_scaled, y_test)
        
        self.trained = True
        
        print(f"✅ Training complete!")
        print(f"   Train accuracy: {train_acc*100:.2f}%")
        print(f"   Test accuracy: {test_acc*100:.2f}%")
        
        return {
            'train_accuracy': train_acc,
            'test_accuracy': test_acc,
            'samples': n_samples
        }
    
    def predict(self, applicant_data):
        """Predict eligibility"""
        if not self.trained:
            raise Exception("Model not trained. Call train() first.")
        
        # Extract features in correct order
        features = np.array([[
            applicant_data['income'],
            applicant_data['family_size'],
            applicant_data['age'],
            applicant_data['dependents'],
            applicant_data['location'],
            applicant_data['land_acres'],
            applicant_data['bank_balance'],
            applicant_data['has_vehicle']
        ]])
        
        features_scaled = self.scaler.transform(features)
        
        prediction = self.model.predict(features_scaled)[0]
        probabilities = self.model.predict_proba(features_scaled)[0]
        confidence = max(probabilities) * 100
        
        # Feature importance for explainability
        importance = dict(zip(self.feature_names, self.model.feature_importances_))
        
        # Generate reasoning
        reasoning = self._generate_reasoning(applicant_data, importance, prediction)
        
        # Determine if manual review needed
        needs_review = confidence < 75 or len(reasoning) > 5
        
        decision = 'APPROVED' if prediction == 1 else 'REJECTED'
        if needs_review:
            decision = 'PENDING_REVIEW'
        
        return {
            'decision': decision,
            'confidence': round(confidence, 2),
            'reasoning': reasoning,
            'top_factors': sorted(importance.items(), key=lambda x: x[1], reverse=True)[:3],
            'needs_manual_review': needs_review
        }
    
    def _generate_reasoning(self, data, importance, prediction):
        """Generate human-readable explanation"""
        reasons = []
        
        # Positive factors
        if data['income'] < 100000:
            reasons.append(f"✓ Low annual income (₹{data['income']:,})")
        
        if data['family_size'] > 4:
            reasons.append(f"✓ Large family size ({data['family_size']} members)")
        
        if data['dependents'] > 2:
            reasons.append(f"✓ Multiple dependents ({data['dependents']})")
        
        if data['location'] == 1:
            reasons.append("✓ Rural location (priority area)")
        elif data['location'] == 2:
            reasons.append("✓ Tribal location (high priority)")
        
        if data['age'] > 60:
            reasons.append(f"✓ Senior citizen (age {data['age']})")
        elif data['age'] < 25:
            reasons.append(f"✓ Young applicant (age {data['age']})")
        
        if data['land_acres'] < 2:
            reasons.append(f"✓ Limited land ownership ({data['land_acres']:.1f} acres)")
        
        # Negative factors
        if data['bank_balance'] > 500000:
            reasons.append(f"⚠ High bank balance (₹{data['bank_balance']:,})")
        
        if data['has_vehicle'] and data['income'] < 50000:
            reasons.append("⚠ Income-asset mismatch (owns vehicle)")
        
        if data['land_acres'] > 5:
            reasons.append(f"⚠ Significant land ownership ({data['land_acres']:.1f} acres)")
        
        return reasons
    
    def save(self, model_path='models/welfare_model.pkl'):
        """Save trained model"""
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        joblib.dump(self.model, model_path)
        joblib.dump(self.scaler, model_path.replace('.pkl', '_scaler.pkl'))
        print(f"💾 Model saved to {model_path}")
    
    def load(self, model_path='models/welfare_model.pkl'):
        """Load pre-trained model"""
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model not found at {model_path}. Train first.")
        
        self.model = joblib.load(model_path)
        self.scaler = joblib.load(model_path.replace('.pkl', '_scaler.pkl'))
        self.trained = True
        print(f"✅ Model loaded from {model_path}")