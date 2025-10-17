import hashlib
import json
from time import time
import requests

class Block:
    """
    Represents a single block in the blockchain.
    """
    def __init__(self, index, timestamp, data, proof, previous_hash):
        """
        Constructs a new Block.

        :param index: The index of this block in the chain.
        :param timestamp: The time of block creation.
        :param data: The data to be stored (e.g., medical records).
        :param proof: The proof of work number that resulted in this block.
        :param previous_hash: The hash of the previous block in the chain.
        """
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.proof = proof
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        """
        Calculates the SHA-256 hash of the block.
        The block's dictionary is converted to a sorted JSON string to ensure
        consistent hashes.
        """
        block_string = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "proof": self.proof,
            "previous_hash": self.previous_hash
        }, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

class Blockchain:
    """
    Manages the entire blockchain, including the chain itself, pending data,
    and the network of nodes.
    """
    def __init__(self):
        """
        Constructs a new Blockchain, initializes the chain, pending data,
        and node set, and creates the genesis block.
        """
        self.chain = []
        self.pending_data = []
        self.nodes = set()
        self.difficulty = 4
        # Create the very first block in the chain
        print("Creating genesis block...")
        self.create_block(previous_hash="0", data={"patient_id": "Genesis", "details": "First Block"}, proof=100)

    def create_block(self, data, previous_hash, proof):
        """
        Creates a new block and adds it to the chain.

        :param data: The data to be included in the new block.
        :param previous_hash: The hash of the block before this one.
        :param proof: The proof of work for this new block.
        :return: The newly created Block object.
        """
        block = Block(
            index=len(self.chain),
            timestamp=time(),
            data=data,
            proof=proof,
            previous_hash=previous_hash
        )
        # Reset the list of pending data now that it's been added to a block
        self.pending_data = []
        self.chain.append(block)
        return block

    def add_data(self, data):
        """
        Adds new data to the list of pending data to be included in the next block.

        :param data: The data to add (e.g., a new medical record).
        :return: The index of the block that will hold this data.
        """
        self.pending_data.append(data)
        return self.get_last_block().index + 1

    def get_last_block(self):
        """
        A simple helper method to return the last block in the chain.
        """
        return self.chain[-1]


    def is_valid_proof(self, last_proof, proof):
        """
        Validates a proof of work against the current difficulty.
        """
        # Create the target string of zeros based on the current difficulty
        target = '0' * self.difficulty

        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()

        # Check if the hash starts with the required number of zeros
        return guess_hash[:self.difficulty] == target

    def proof_of_work(self, last_proof):
        """
        Finds a number 'proof' that, when hashed with the previous proof,
        produces a hash with 4 leading zeros.

        :param last_proof: The proof from the previous block.
        :return: The new, valid proof number.
        """
        proof = 0
        while not self.is_valid_proof(last_proof, proof):
            proof += 1
        return proof

    def register_node(self, address):
        """
        Adds a new node's address to the list of nodes.

        :param address: The address of the node (e.g., '127.0.0.1:5001').
        """
        self.nodes.add(address)

    def valid_chain(self, chain):
        """
        Determines if a given blockchain is valid by checking hashes and proofs.

        :param chain: A list of block dictionaries.
        :return: True if the chain is valid, False otherwise.
        """
        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            
            # Check if the previous_hash link is correct
            if block['previous_hash'] != last_block['hash']:
                return False

            # Check if the proof of work is valid
            if not self.is_valid_proof(last_block['proof'], block['proof']):
                return False

            last_block = block
            current_index += 1
        return True

    def resolve_conflicts(self):
        """
        The consensus algorithm. It resolves conflicts by replacing our chain
        with the longest valid chain in the network.

        :return: True if our chain was replaced, False otherwise.
        """
        neighbours = self.nodes
        new_chain = None
        max_length = len(self.chain)

        # Grab and verify the chains from all other nodes in the network
        for node_address in neighbours:
            try:
                response = requests.get(f'http://{node_address}/chain')
                if response.status_code == 200:
                    length = response.json()['length']
                    chain_data = response.json()['chain']

                    # Check if the neighbor's chain is longer and valid
                    if length > max_length and self.valid_chain(chain_data):
                        max_length = length
                        new_chain = chain_data
            except requests.exceptions.RequestException as e:
                print(f"Could not connect to node {node_address}: {e}")

        # If we found a longer, valid chain, replace ours
        if new_chain:
            # Reconstruct the chain using Block objects from the dictionary data
            self.chain = [Block(b['index'], b['timestamp'], b['data'], b['proof'], b['previous_hash']) for b in new_chain]
            return True

        return False