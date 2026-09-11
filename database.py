# database.py
import sqlite3
import json
from datetime import datetime

class Database:
    def __init__(self, db_name='welfare.db'):
        self.db_name = db_name
        self.init_db()
    
    def init_db(self):
        """Create all tables"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Applications table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                app_id TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                aadhaar TEXT NOT NULL,
                income INTEGER NOT NULL,
                family_size INTEGER NOT NULL,
                age INTEGER NOT NULL,
                dependents INTEGER NOT NULL,
                location INTEGER NOT NULL,
                land_acres REAL NOT NULL,
                bank_balance INTEGER NOT NULL,
                has_vehicle INTEGER NOT NULL,
                
                -- AI Decision fields
                ai_decision TEXT NOT NULL,
                ai_confidence REAL NOT NULL,
                ai_reasoning TEXT,
                fraud_flags TEXT,
                
                -- Status tracking
                status TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                reviewed_at TIMESTAMP,
                reviewed_by TEXT,
                
                -- Blockchain reference
                blockchain_hash TEXT
            )
        ''')
        
        # Reviews table (officer feedback for "learning")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                app_id TEXT NOT NULL,
                officer_id TEXT NOT NULL,
                officer_decision TEXT NOT NULL,
                officer_comments TEXT,
                ai_was_correct INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (app_id) REFERENCES applications (app_id)
            )
        ''')
        
        # Blockchain records
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS blockchain (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                block_index INTEGER NOT NULL,
                timestamp REAL NOT NULL,
                data TEXT NOT NULL,
                previous_hash TEXT NOT NULL,
                hash TEXT NOT NULL,
                nonce INTEGER NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_application(self, app_data):
        """Insert new application"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO applications (
                app_id, name, aadhaar, income, family_size, age,
                dependents, location, land_acres, bank_balance, has_vehicle,
                ai_decision, ai_confidence, ai_reasoning, fraud_flags, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            app_data['app_id'], app_data['name'], app_data['aadhaar'],
            app_data['income'], app_data['family_size'], app_data['age'],
            app_data['dependents'], app_data['location'], app_data['land_acres'],
            app_data['bank_balance'], app_data['has_vehicle'],
            app_data['ai_decision'], app_data['ai_confidence'],
            json.dumps(app_data['ai_reasoning']), json.dumps(app_data['fraud_flags']),
            app_data['status']
        ))
        
        conn.commit()
        conn.close()
        return app_data['app_id']
    
    def get_application(self, app_id):
        """Get single application"""
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM applications WHERE app_id = ?', (app_id,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return dict(result)
        return None
    
    def get_all_applications(self, status_filter=None):
        """Get all applications with optional filter"""
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if status_filter:
            cursor.execute('SELECT * FROM applications WHERE status = ? ORDER BY created_at DESC', (status_filter,))
        else:
            cursor.execute('SELECT * FROM applications ORDER BY created_at DESC')
        
        results = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in results]
    
    def update_application_review(self, app_id, officer_id, decision, comments):
        """Update application after officer review"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE applications 
            SET status = ?, reviewed_at = ?, reviewed_by = ?
            WHERE app_id = ?
        ''', (decision, datetime.now(), officer_id, app_id))
        
        # Add to reviews table
        cursor.execute('''
            INSERT INTO reviews (app_id, officer_id, officer_decision, officer_comments)
            VALUES (?, ?, ?, ?)
        ''', (app_id, officer_id, decision, comments))
        
        conn.commit()
        conn.close()
    
    def add_blockchain_record(self, block_data):
        """Add blockchain record"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO blockchain (block_index, timestamp, data, previous_hash, hash, nonce)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            block_data['index'], block_data['timestamp'], 
            json.dumps(block_data['data']), block_data['previous_hash'],
            block_data['hash'], block_data['nonce']
        ))
        
        conn.commit()
        conn.close()
    
    def get_blockchain(self):
        """Get entire blockchain"""
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM blockchain ORDER BY block_index')
        results = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in results]
    
    def get_stats(self):
        """Get dashboard statistics"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        stats = {}
        
        cursor.execute('SELECT COUNT(*) FROM applications')
        stats['total'] = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM applications WHERE status = "APPROVED"')
        stats['approved'] = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM applications WHERE status = "PENDING_REVIEW"')
        stats['pending'] = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM applications WHERE status = "REJECTED"')
        stats['rejected'] = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM applications WHERE fraud_flags != "[]"')
        stats['fraud_flagged'] = cursor.fetchone()[0]
        
        conn.close()
        return stats
    
def generate_app_id():
    """Generate unique application ID"""
    import random, string
    timestamp = datetime.now().strftime('%Y%m%d')
    random_part = ''.join(random.choices(string.digits, k=4))
    return f"APP-{timestamp}-{random_part}"