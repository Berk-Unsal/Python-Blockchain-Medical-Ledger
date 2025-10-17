import sys
import uuid
from flask import Flask, jsonify, request, render_template

# Import the Blockchain class from our other file
from blockchain import Blockchain

# --- APP SETUP ---
app = Flask(__name__)

# Generate a globally unique address for this node
node_identifier = str(uuid.uuid4()).replace('-', '')

# Instantiate the Blockchain
blockchain = Blockchain()

# --- API ENDPOINTS ---

@app.route('/')
def index():
    """Serves the user interface."""
    return render_template('index.html')

@app.route('/mine', methods=['GET'])
def mine():
    """
    Runs the proof of work algorithm to find the next proof, rewards the miner,
    and adds the new block to the chain.
    """
    last_block = blockchain.get_last_block()
    last_proof = last_block.proof
    proof = blockchain.proof_of_work(last_proof)

    # Reward the miner by adding a transaction. Sender "0" signifies a new coin.
    blockchain.add_data(
        data={"sender": "0", "recipient": node_identifier, "details": "Mining Reward"}
    )

    # Forge the new Block by adding it to the chain
    previous_hash = last_block.hash
    block = blockchain.create_block(blockchain.pending_data, previous_hash, proof)

    response = {
        'message': "New Block Forged",
        'index': block.index,
        'data': block.data,
        'proof': block.proof,
        'previous_hash': block.previous_hash,
    }
    return jsonify(response), 200

@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    """
    Receives new medical record data as a POST request and adds it to the
    list of pending data.
    """
    values = request.get_json(force=True)
    if not values:
        return "Error: Invalid or empty JSON provided", 400

    # Check that the required fields are in the POST'd data
    required = ['patient_id', 'details']
    if not all(k in values for k in required):
        return 'Missing required JSON values: patient_id, details', 400

    # Add the new data to the pending list
    index = blockchain.add_data(values)
    response = {'message': f'Transaction will be added to Block {index}'}
    return jsonify(response), 201

@app.route('/chain', methods=['GET'])
def full_chain():
    """Returns the full, current blockchain as JSON."""
    chain_data = []
    for block in blockchain.chain:
        # Convert our Block objects to dictionaries to be serializable
        chain_data.append(block.__dict__)
        
    response = {
        'chain': chain_data,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200

@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    """
    Accepts a list of new nodes in the form of URLs and registers them.
    """
    values = request.get_json(force=True)
    nodes = values.get('nodes')
    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400

    for node in nodes:
        blockchain.register_node(node)

    response = {
        'message': 'New nodes have been added',
        'total_nodes': list(blockchain.nodes),
    }
    return jsonify(response), 201

@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    """
    Runs the consensus algorithm to resolve any conflicts and ensure the node
    has the correct chain.
    """
    replaced = blockchain.resolve_conflicts()

    if replaced:
        response = {
            'message': 'Our chain was replaced by the authoritative one.',
            'new_chain': [block.__dict__ for block in blockchain.chain]
        }
    else:
        response = {
            'message': 'Our chain is authoritative.',
            'chain': [block.__dict__ for block in blockchain.chain]
        }
    return jsonify(response), 200

@app.route('/nodes/get', methods=['GET'])
def get_nodes():
    """Returns the list of known nodes."""
    nodes = list(blockchain.nodes)
    response = {'nodes': nodes}
    return jsonify(response), 200

# In api.py, add these two new endpoints

@app.route('/difficulty', methods=['GET'])
def get_difficulty():
    """Returns the current mining difficulty."""
    response = {'difficulty': blockchain.difficulty}
    return jsonify(response), 200

@app.route('/difficulty', methods=['POST'])
def set_difficulty():
    """Sets a new mining difficulty."""
    values = request.get_json(force=True)
    if not values or 'difficulty' not in values:
        return 'Error: Missing "difficulty" in request body', 400
    
    try:
        new_difficulty = int(values['difficulty'])
        if new_difficulty < 1:
            return 'Difficulty must be a positive integer.', 400
        
        blockchain.difficulty = new_difficulty
        response = {
            'message': f'Mining difficulty set to {new_difficulty}',
            'difficulty': new_difficulty
        }
        return jsonify(response), 200
    except (ValueError, TypeError):
        return 'Invalid difficulty provided. Must be an integer.', 400

# --- SERVER EXECUTION ---
if __name__ == '__main__':
    # Get the port from the command-line arguments, default to 5000
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
    app.run(host='0.0.0.0', port=port)