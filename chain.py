import hashlib 
import json
from time import time
from uuid import uuid4

from flask import Flask, jsonify, request

class Blockchain(object):
    def __init__(self): 
        self.chain = []
        self.current_transactions = []

        # genesis block
        self.new_block(previous_hash=1, proof=100)
    
    def proof_of_work(self, last_proof):
        # we can make any PoW algo here, but for now its 
        # - Find a number p' such that hash(pp') contains leading 4 zeroes, where p is the previous p'
        #  - p is the previous proof, and p' is the new proof
        proof = 0

        while self.valid_proof(last_proof, proof) is False:
            proof += 1

        return proof

    def new_block(self, proof, previous_hash=None):
        # Creates a new block and adds to chain
        
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1])
        }

        # Reset

        self.current_transactions = []
        self.chain.append(block)
        return block

    def new_transaction(self, sender, recipient, amount):
        # Adds a new transaction to the list of transactions
        
        self.current_transactions.append({
            'sender':sender,
            'recipient': recipient,
            'amount': amount
        })

        return self.last_block['index'] + 1
        # increments the last block of the chain 

    @staticmethod
    def hash(block):
        # Hashes a block
        # Creates a SHA-256 hash of a block
        
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest() 
    
    @property
    def last_block(self):
        # returns the last block of the chain.  
        return self.chain[-1]
    
    @staticmethod
    def valid_proof(last_proof, proof):
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

app = Flask(__name__)

node_id = str(uuid4()).replace('-', '')
chain = Blockchain()

@app.route('/mine', methods=['GET'])
def mine():
    last_block = chain.last_block
    last_proof = last_block['proof']
    proof = chain.proof_of_work(last_proof)

    chain.new_transaction(
        sender="0",
        recipient=node_id,
        amount=1
    )
    previous_hash = chain.hash(last_block)
    block = chain.new_block(proof, previous_hash)

    response = {
        'message': "New Block Forged",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }

    return jsonify(response), 200

@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()

    required = ['sender', 'recipient', 'amount']
    # if we are missing any values from requirement
    if not all(k in values for k in required):
        return 'Missing values', 400
    
    index = chain.new_transaction(values['sender'], values['recipient'], values['amount'])
    response = {'message': f'Transaction will be added to the Block {index}'}
    return jsonify(response), 201

@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': chain.chain,
        'length': len(chain.chain)
    }
    return jsonify(response), 200 

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
