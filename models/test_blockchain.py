import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))  # add parent folder to path

from database import Database
from models.blockchain import SimpleBlockchain

import time

def test_blockchain():
    print("🧪 Testing Blockchain...")
    
    # Initialize
    db = Database('test_blockchain.db')
    blockchain = SimpleBlockchain(db)
    
    print("\n1. Testing Genesis Block...")
    chain = db.get_blockchain()
    assert len(chain) > 0, "Genesis block not created"
    print("   ✅ Genesis block exists")
    
    print("\n2. Testing Add Block...")
    test_data = {
        'app_id': 'APP-TEST-001',
        'decision': 'APPROVED',
        'officer': 'OFFICER-001',
        'timestamp': time.time()
    }
    
    new_block = blockchain.add_block(test_data)
    print(f"   Block added with hash: {new_block['hash'][:16]}...")
    assert new_block['hash'].startswith('0' * blockchain.difficulty)
    print("   ✅ Block added successfully")
    
    print("\n3. Testing Chain Validation...")
    is_valid = blockchain.validate_chain()
    assert is_valid == True
    print("   ✅ Chain is valid")
    
    print("\n4. Testing Chain Info...")
    info = blockchain.get_chain_info()
    print(f"   Total blocks: {info['total_blocks']}")
    print(f"   Is valid: {info['is_valid']}")
    print("   ✅ Chain info working")
    
    print("\n5. Testing Multiple Blocks...")
    for i in range(3):
        blockchain.add_block({'test': f'block_{i}'})
    
    chain = db.get_blockchain()
    assert len(chain) >= 5  # Genesis + 1 test + 3 more
    print(f"   ✅ Added multiple blocks: {len(chain)} total")
    
    print("\n✅ All blockchain tests passed!")

if __name__ == "__main__":
    test_blockchain()