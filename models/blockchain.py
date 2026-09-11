import hashlib
import json
import time

class SimpleBlockchain:
    def __init__(self, database):
        self.database = database
        self.difficulty = 2  # Number of leading zeros required
        
        # Create genesis block if blockchain is empty
        existing_chain = self.database.get_blockchain()
        if len(existing_chain) == 0:
            self.create_genesis_block()
    
    def create_genesis_block(self):
        """Create the first block"""
        genesis_block = {
            'index': 0,
            'timestamp': time.time(),
            'data': {'message': 'Genesis Block - Welfare Distribution System'},
            'previous_hash': '0',
            'nonce': 0
        }
        genesis_block['hash'] = self.calculate_hash(genesis_block)
        
        self.database.add_blockchain_record(genesis_block)
        print("✅ Genesis block created")
    
    def calculate_hash(self, block):
        """Calculate SHA-256 hash of block"""
        block_string = json.dumps({
            'index': block['index'],
            'timestamp': block['timestamp'],
            'data': block['data'],
            'previous_hash': block['previous_hash'],
            'nonce': block['nonce']
        }, sort_keys=True).encode()
        
        return hashlib.sha256(block_string).hexdigest()
    
    def get_latest_block(self):
        """Get the most recent block"""
        chain = self.database.get_blockchain()
        if len(chain) == 0:
            return None
        return chain[-1]
    
    def proof_of_work(self, block):
        """Simple proof of work - find nonce that creates hash with leading zeros"""
        block['nonce'] = 0
        computed_hash = self.calculate_hash(block)
        
        while not computed_hash.startswith('0' * self.difficulty):
            block['nonce'] += 1
            computed_hash = self.calculate_hash(block)
        
        return computed_hash
    
    def add_block(self, data):
        """Add a new block to the blockchain"""
        latest_block = self.get_latest_block()
        
        if latest_block is None:
            print("⚠ No genesis block found, creating one...")
            self.create_genesis_block()
            latest_block = self.get_latest_block()
        
        new_block = {
            'index': latest_block['block_index'] + 1,
            'timestamp': time.time(),
            'data': data,
            'previous_hash': latest_block['hash'],
            'nonce': 0
        }
        
        # Perform proof of work
        new_block['hash'] = self.proof_of_work(new_block)
        
        # Save to database
        self.database.add_blockchain_record(new_block)
        
        return new_block
    
    def validate_chain(self):
        """Verify blockchain integrity"""
        chain = self.database.get_blockchain()
        
        if len(chain) == 0:
            return True
        
        for i in range(1, len(chain)):
            current_block = chain[i]
            previous_block = chain[i-1]
            
            # Check if current block's previous_hash matches previous block's hash
            if current_block['previous_hash'] != previous_block['hash']:
                print(f"❌ Chain broken at block {i}: Hash mismatch")
                return False
            
            # Recalculate hash to verify
            block_copy = {
                'index': current_block['block_index'],
                'timestamp': current_block['timestamp'],
                'data': json.loads(current_block['data']),
                'previous_hash': current_block['previous_hash'],
                'nonce': current_block['nonce']
            }
            
            if self.calculate_hash(block_copy) != current_block['hash']:
                print(f"❌ Block {i} has been tampered with")
                return False
        
        return True
    
    def get_chain_info(self):
        """Get blockchain statistics"""
        chain = self.database.get_blockchain()
        
        return {
            'total_blocks': len(chain),
            'is_valid': self.validate_chain(),
            'latest_block_hash': chain[-1]['hash'] if chain else None,
            'genesis_timestamp': chain[0]['timestamp'] if chain else None
        }
