import hashlib
import json


class MerkleTree:
    def __init__(self, data):
        self.leaves = data
        self.root = None

    def build(self):
        if len(self.leaves) == 1:
            self.root = self.leaves[0]
            return
        if len(self.leaves) % 2 != 0:
            self.leaves.append(self.leaves[-1])
        self.leaves = [
            hashlib.sha256(json.dumps(s, sort_keys=True).encode()).hexdigest()
            for s in self.leaves
        ]
        self.leaves = [self.leaves[i : i + 2] for i in range(0, len(self.leaves), 2)]
        self.leaves = [
            self.leaves[0][0] + self.leaves[0][1]
            if len(self.leaves[0]) == 2
            else self.leaves[0][0]
            for self.leaves[0] in self.leaves
        ]
        self.build()

    def get_root(self):
        root = json.dumps(self.root, sort_keys=True).encode()
        return hashlib.sha256(root).hexdigest()


if __name__ == "__main__":
    data = [1, 2, 3, 4, 5, 6]
    tree = MerkleTree(data)
    tree.build()
    print(tree.get_root())
