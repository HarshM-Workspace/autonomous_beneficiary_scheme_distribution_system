from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_cors import CORS
from database import Database, generate_app_id
from models.ml_model import WelfareEligibilityAI
from models.fraud_detector import FraudDetector
from models.blockchain import SimpleBlockchain
import json

app = Flask(__name__)
CORS(app)

# Initialize components
db = Database()
ai_model = WelfareEligibilityAI()
fraud_detector = FraudDetector()
blockchain = SimpleBlockchain(db)

# Load pre-trained model
try:
    ai_model.load()
    print("✅ AI model loaded")
except FileNotFoundError:
    print("⚠ Model not found. Training new model...")
    ai_model.train()
    ai_model.save()

# ===================
# ROUTES
# ===================

@app.route('/')
def index():
    """Application form page"""
    return render_template('index.html')

@app.route('/apply', methods=['POST'])
def apply():
    """Handle application submission"""
    try:
        # Get form data
        form_data = {
            'name': request.form.get('name'),
            'aadhaar': request.form.get('aadhaar'),
            'income': int(request.form.get('income')),
            'family_size': int(request.form.get('family_size')),
            'age': int(request.form.get('age')),
            'dependents': int(request.form.get('dependents')),
            'location': int(request.form.get('location')),
            'land_acres': float(request.form.get('land_acres', 0)),
            'bank_balance': int(request.form.get('bank_balance', 0)),
            'has_vehicle': int(request.form.get('has_vehicle', 0))
        }
        
        # Generate unique app ID
        app_id = generate_app_id()
        
        # Run AI eligibility check
        ai_result = ai_model.predict(form_data)
        
        # Check for fraud
        fraud_result = fraud_detector.check_fraud(form_data)
        
        # Add to fraud detector database
        fraud_detector.add_application(app_id, form_data)
        
        # Override decision if fraud detected
        if fraud_result['is_fraud'] and len(fraud_result['flags']) > 0:
            if any('CRITICAL' in flag for flag in fraud_result['flags']):
                ai_result['decision'] = 'REJECTED'
            else:
                ai_result['decision'] = 'PENDING_REVIEW'
        
        # Prepare application data
        app_data = {
            'app_id': app_id,
            **form_data,
            'ai_decision': ai_result['decision'],
            'ai_confidence': ai_result['confidence'],
            'ai_reasoning': ai_result['reasoning'],
            'fraud_flags': fraud_result['flags'],
            'status': ai_result['decision']
        }
        
        # Save to database
        db.add_application(app_data)
        
        # If auto-approved/rejected, add to blockchain immediately
        if ai_result['decision'] in ['APPROVED', 'REJECTED'] and not fraud_result['is_fraud']:
            blockchain_data = {
                'app_id': app_id,
                'decision': ai_result['decision'],
                'confidence': ai_result['confidence'],
                'officer': 'AI_AUTO',
                'timestamp': 'auto'
            }
            block = blockchain.add_block(blockchain_data)
        
        return render_template('success.html', app_id=app_id, decision=ai_result['decision'])
    
    except Exception as e:
        print(f"Error in apply: {e}")
        return render_template('error.html', error=str(e)), 500

@app.route('/dashboard')
def dashboard():
    """Officer dashboard"""
    # Get filter from query params
    status_filter = request.args.get('filter', None)
    
    applications = db.get_all_applications(status_filter)
    stats = db.get_stats()
    
    # Parse JSON strings back to lists
    for app in applications:
        app['ai_reasoning'] = json.loads(app['ai_reasoning']) if app['ai_reasoning'] else []
        app['fraud_flags'] = json.loads(app['fraud_flags']) if app['fraud_flags'] else []
    
    return render_template('dashboard.html', 
                         applications=applications, 
                         stats=stats)

@app.route('/review/<app_id>', methods=['POST'])
def review(app_id):
    """Officer review decision"""
    try:
        decision = request.form.get('decision')  # 'APPROVED' or 'REJECTED'
        comments = request.form.get('comments', '')
        officer_id = request.form.get('officer_id', 'OFFICER-DEFAULT')
        
        # Update database
        db.update_application_review(app_id, officer_id, decision, comments)
        
        # Add to blockchain
        blockchain_data = {
            'app_id': app_id,
            'decision': decision,
            'officer': officer_id,
            'comments': comments,
            'timestamp': 'reviewed'
        }
        blockchain.add_block(blockchain_data)
        
        return redirect(url_for('dashboard'))
    
    except Exception as e:
        print(f"Error in review: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/track')
def track_page():
    """Status tracking page"""
    return render_template('track.html')

@app.route('/status/<app_id>')
def status(app_id):
    """Get application status"""
    app = db.get_application(app_id)
    
    if not app:
        return render_template('track.html', error='Application not found')
    
    # Parse JSON fields
    app['ai_reasoning'] = json.loads(app['ai_reasoning']) if app['ai_reasoning'] else []
    app['fraud_flags'] = json.loads(app['fraud_flags']) if app['fraud_flags'] else []
    
    return render_template('status.html', app=app)

@app.route('/blockchain-view')
def blockchain_view():
    """Blockchain viewer page"""
    chain = db.get_blockchain()
    info = blockchain.get_chain_info()
    
    # Parse data field
    for block in chain:
        block['data'] = json.loads(block['data']) if isinstance(block['data'], str) else block['data']
    
    return render_template('blockchain.html', 
                         chain=chain, 
                         info=info)

@app.route('/api/stats')
def api_stats():
    """API endpoint for stats"""
    stats = db.get_stats()
    chain_info = blockchain.get_chain_info()
    
    return jsonify({
        'applications': stats,
        'blockchain': chain_info
    })

@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', error='Page not found'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', error='Internal server error'), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
