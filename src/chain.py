from atexit import register
import hashlib
import json
from time import time
from urllib import response
from urllib.parse import urlparse
from uuid import uuid4

import requests
from flask import Flask, redirect
from flask import jsonify
from flask import request
from flask_cors import CORS

from merkle import MerkleTree
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument("-p", "--port", default=5000, type=int, help="port to listen on")
args = parser.parse_args()
port = args.port


class Robucks(object):

    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.nodes = set()
        self.amount = 0

        # genesis block
        self.new_block(previous_hash=1, proof=100)

    def new_block(self, proof: int, previous_hash: any = None) -> dict:
        """
        Create a new Block in the Blockchain
        :param proof: <int> The proof given by the Proof of Work algorithm
        :param previous_hash: (Optional) <str> Hash of previous Block
        :return: <dict> New Block
        """
        # handles the genisis block
        if len(self.current_transactions) > 0:
            merkle = MerkleTree(self.current_transactions)
            merkle.build()
            merkle_root = merkle.get_root()
        else:
            merkle_root = None

        # Creates a new block and adds to chain
        block = {
            "index": len(self.chain) + 1,
            "timestamp": time(),
            "merkle_root_hash": merkle_root,
            "proof": proof,
            "previous_hash": previous_hash or self.hash(self.chain[-1]),
            "state": None
        }

        # Reset

        self.current_transactions = []
        self.chain.append(block)
        return block

    def new_transaction(self, sender: str, recipient: str, amount: int) -> int:
        """
        Creates a new transaction to go into the next mined Block
        :param sender: <str> Address of the Sender
        :param recipient: <str> Address of the Recipient
        :param amount: <int> Amount
        :return: <int> The index of the Block that will hold this transaction
        """
        # Adds a new transaction to the list of transactions
        # hash of the transaction is the hash of the sender, recipient and amount
        # using merkle trees to verify the integrity of the transaction

        self.current_transactions.append({
            "sender": sender,
            "recipient": recipient,
            "amount": amount
        })

        self.amount += amount

        # reward system
        if self.last_block["index"] % 4413 == 0:
            self.current_transactions.append({
                "sender": "0",
                "recipient": sender,
                "amount": 100
            })

            self.amount += 100

        # limit
        if self.amount > 21 * 10**6:
            self.current_transactions = []
            # handle the case where the amount is greater than 21 million
            # reset the current transactions
            # something where /mine will not work.

        return self.last_block["index"] + 1
        # increments the last block of the chain

    @staticmethod
    def hash(block: dict) -> str:
        """
        Creates a SHA-256 hash of a Block
        :param block: <dict> Block
        :return: <str>
        """
        # Hashes a block
        # Creates a SHA-256 hash of a block

        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        """
        Returns the last Block in the chain
        :return: <dict> last Block
        """
        # returns the last block of the chain.
        return self.chain[-1]

    def proof_of_work(self, last_proof: int) -> int:
        """
        Simple Proof of Work Algorithm:
         - Find a number p' such that hash(pp') contains leading 4 zeroes, where p is the previous p'
         - p is the previous proof, and p' is the new proof
        :param last_proof: <int>
        :return: <int>
        """

        proof = 0

        while self.valid_proof(last_proof, proof) is False:
            proof += 1

        return proof

    @staticmethod
    def valid_proof(last_proof: int, proof: int) -> bool:
        """
        Validates the Proof: Does hash(last_proof, proof) contain 4 leading zeroes?
        :param last_proof: <int> Previous Proof
        :param proof: <int> Current Proof
        :return: <bool> True if correct, False if not.
        """

        guess = f"{last_proof}{proof}".encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

    def register_node(self, address: str, identifier: str) -> None:
        """
        Add a new node to the list of nodes
        :param address: <str> Address of node. Eg. 'http://
        :return: None
        """
        
        # adding a new list of nodes
        parsed_url = urlparse(address)
        with open('nodes.txt', 'a') as f:
            if parsed_url.netloc:
                f.write(f"{parsed_url.netloc} {identifier}" +  '\n')
            elif parsed_url.path:
                # Accepts an URL without scheme like '192.168.0.5:5000'.
                f.write(f"{parsed_url.path} {identifier}" +  '\n')
            else:
                raise ValueError("Invalid URL")

    def valid_chain(self, chain: list) -> bool:
        """
        Determine if a given blockchain is valid
        :param chain: <list> A blockchain
        :return: <bool> True if valid, False if not


        Ethereum WhitePaper:
        A valid block is a block that satisfies the following conditions:
        1. Check if the previous block is referenced by the current block.
        2. Check that the timestamp is not greater than the previous block and is not in the future. (less than 2 hours into the future)
        3. Check that the proof of work is valid.
        4. let S[0] be the state at the end of the previous block. ???
        5. Suppose that TX is the list of transactions in the current block. with n transactions, the state after the nth transaction is S[n].
        for i in range(0, n-1):
            S[i+1] = S[i] + TX[i]
        6. Return true if S[n] is valid and register S[n], false otherwise.
        """

        last_block = chain[0]
        current_index = 1

        # Loop through each block and verifing both hash and proof
        while current_index < len(chain):
            block = chain[current_index]

            if block["previous_hash"] != self.hash(last_block):
                return False

            if not self.valid_proof(last_block["proof"], block["proof"]):
                return False

            if block['timestamp'] >= time() + 2*60**2 or \
                block['timestamp'] >= last_block['timestamp']:
                return False
            
            # compare merkle root of the block with the merkle root of the transactions

            if \
             block['merkle_root'] != self.merkle_root(block['transactions']):
                return False

            last_block = block
            current_index += 1
        return True

    def resolve_conflicts(self):
        """
        This is our Consensus Algorithm, it resolves conflicts
        by replacing our chain with the longest one in the network.
        :return: <bool> True if our chain was replaced, False if not
        """
        """
        replaces chain with the longest one on our network
        therefore resolving conflicts that may turn up

        Visites all neighbouring nodes and using valid chain will verify
        whether the chain is valid and if the length of the chain is greater
        then it will replace the chain.
        """


        neighbors = self.nodes
        new_chain = None

        max_length = len(self.chain)
        # verify each chain from each node
        for node in neighbors:
            response = requests.get(f"http://{node}/chain")

            if response.status_code == 200:
                length = response.json()["length"]
                chain = response.json()["chain"]

                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain
        if new_chain:
            self.chain = new_chain
            return True

        return False


app = Flask(__name__)
CORS(app)

node_id = str(uuid4()).replace("-", "")
chain = Robucks()

@app.route('/')
def index():

    checking = True
    if checking:
        host = 'http://127.0.0.1:' + str(port)
        chain.register_node(host, node_id)

        # TODO if nodes.txt is not empty then read it and add to the chain
        with open('nodes.txt', 'r') as f:
            for line in f:
                node, _ = line.strip().split(' ')
                chain.nodes.add(node)
        checking = False
    return redirect('/chain', code=302, Response=None, headers={'Location': '/chain'})

@app.route("/mine", methods=["GET"])
def mine():
    last_block = chain.last_block
    last_proof = last_block["proof"]
    proof = chain.proof_of_work(last_proof)

    chain.new_transaction(sender="0", recipient=node_id, amount=1)
    previous_hash = chain.hash(last_block)
    block = chain.new_block(proof, previous_hash)

    # checks whether there is a longer chain.
    # TODO find a way to keep transactions

    """
    When a Chain is a replaced, a chain may hold a transaction that is not
    been broadcasted to the network. Need to check whether that is not the case
    """
    
    replaced = chain.resolve_conflicts()

    response = {
        "message": "New Block Forged",
        "index": block["index"],
        "merkle_root_hash": block["merkle_root_hash"],
        "proof": block["proof"],
        "previous_hash": block["previous_hash"],
        'replaced': replaced
    }

    return jsonify(response), 200

# TODO: manage UTXO and wallets
# wallets would be the nodes them selves (just hashed)
@app.route("/transactions/new", methods=["POST"])
def new_transaction():
    values = request.get_json()

    required = ["sender", "recipient", "amount"]
    # if we are missing any values from requirement
    if not all(k in values for k in required):
        return "Missing values", 400

    index = chain.new_transaction(values["sender"], values["recipient"],
                                  values["amount"])
    response = {"message": f"Transaction will be added to the Block {index}"}
    return jsonify(response), 201


@app.route("/chain", methods=["GET"])
def full_chain():
    
    response = {"chain": chain.chain, "length": len(chain.chain)}
    return jsonify(response), 200

@app.route("/nodes/get", methods=["GET"])
def get_nodes():
    nodes = list(chain.nodes)
    response = {"nodes": nodes}
    return jsonify(response), 200


@app.route("/nodes/reset", methods=["GET"])
def reset_nodes():
    chain.nodes = set()
    response = {"message": "Nodes have been reset"}
    return jsonify(response), 200


@app.route("/amount", methods=["GET"])
def amount():
    response = {"amount": chain.amount}
    return jsonify(response), 200


# split between flask and blockchain scripts

if __name__ == "__main__":
    app.run(port=port)

# TODO: merkle tree SPV transaction verification