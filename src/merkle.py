import hashlib
import json


class MerkleTree:

    def __init__(self, data: list):
        self.leaves = data
        self.root = None

    def build(self) -> str:

        """
        Builds the merkle tree
        :return: <str> hashed root

        This function is recursive, it will keep calling itself until the list has only one element
        """
        
        if len(self.leaves) == 1:
            self.root = self.leaves[0]
            return

        if len(self.leaves) % 2 != 0:
            self.leaves.append(self.leaves[-1])

        print(self.leaves)
        
        # hashing each value in the list
        self.leaves = [
            hashlib.sha256(json.dumps(s, sort_keys=True).encode()).hexdigest()
            for s in self.leaves
        ]

        # grouping the list in pairs, if the list has an odd number of elements, the last element is duplicated
        self.leaves = [
            self.leaves[i:i + 2] for i in range(0, len(self.leaves), 2)
        ]

        # summing the pairs if they do not have 2 elements, then leave the element as it is. 
        self.leaves = [
            self.leaves[0][0] + self.leaves[0][1]
            if len(self.leaves[0]) == 2 else self.leaves[0][0]
            for self.leaves[0] in self.leaves
        ]
        
        # recursively calling the build function until the list has only one element
        self.build()

    def get_root(self) -> str:
        """
        Returns the root of the merkle tree
        :return: <str> hashed root

        This is assuming that the root is the only element in the list
        therfore, the root is the first element in the list
        """
        if self.root is None:
            self.build()

        root = json.dumps(self.root, sort_keys=True).encode()
        return hashlib.sha256(root).hexdigest()


if __name__ == "__main__":
    data = [1, 2, 3, 4, 5, 6]
    tree = MerkleTree(data)
    print(tree.get_root())
