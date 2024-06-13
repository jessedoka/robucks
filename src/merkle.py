import hashlib
import json
import hashlib

class MerkleTree:
    def __init__(self, data):
        self.leaves = data
        self.root = None
        self.tree = []

        self.hash_function = lambda x: hashlib.sha256(json.dumps(x, sort_keys=True).encode()).hexdigest()
        

    def build(self):
        if len(self.leaves) == 1:
            self.root = self.leaves[0]
            self.tree.append([self.root])
            return

        if len(self.leaves) % 2 != 0:
            self.leaves.append(self.leaves[-1])

        self.leaves = [
            self.hash_function(leaf)
            for leaf in self.leaves
        ]

        self.tree.append(self.leaves)

        while len(self.leaves) > 1:
            if len(self.leaves) % 2 != 0:
                self.leaves.append(self.leaves[-1])

            self.leaves = [
                self.hash_function(self.leaves[i] + self.leaves[i + 1])
                for i in range(0, len(self.leaves), 2)
            ]

            self.tree.append(self.leaves)

        self.root = self.leaves[0]

    def get_root(self):
        if self.root is None:
            self.build()
        return self.root
    
    def generate_proof(self, target):
        if self.root is None:
            self.build()
        
        target_hash = self.hash_function(target)
        proof = []

        idx = self.tree[0].index(target_hash)

        for level in range(len(self.tree) - 1):
            sibling_idx = idx + 1 if idx % 2 == 0 else idx - 1
            sibling_hash = self.tree[level][sibling_idx]
            proof.append((sibling_hash, idx % 2 == 1))
            idx //= 2

        return proof
    

    def verify_proof(self, proof, target, root):
        computed_hash = self.hash_function(target)
        for proof_hash, is_left in proof:
            if is_left:
                print("going left")
                computed_hash = self.hash_function(proof_hash + computed_hash)
            else:
                print("going right")
                computed_hash = self.hash_function(computed_hash + proof_hash)
        return computed_hash == root


if __name__ == "__main__":
    data = ['Alice', 'Bob', 'Charlie', 'Dave', 'Eve']
    tree = MerkleTree(data)
    root = tree.get_root()
    print("Merkle Root:", root)

    target = 'Alice'
    proof = tree.generate_proof(target)
    print("Merkle Proof for Bob:", proof)

    is_valid = tree.verify_proof(proof, target, root)
    print("Is the proof valid?", is_valid)
