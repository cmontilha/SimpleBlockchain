import hashlib
import json
from time import time
from uuid import uuid4
from urllib.parse import urlparse

from flask import Flask, jsonify, request
import requests


class Chain:
    def __init__(self):
        self.chain = []
        self.pending_transactions = []
        self.nodes = set()

        # Gera o bloco gênesis
        self.add_block(previous_hash='1', proof=100)

    def add_node(self, address):
        """
        Adiciona um novo nó à rede
        """
        parsed_url = urlparse(address)
        if parsed_url.netloc:
            self.nodes.add(parsed_url.netloc)
        elif parsed_url.path:
            self.nodes.add(parsed_url.path)
        else:
            raise ValueError('URL inválida')

    def consensus_resolution(self):
        """
        Algoritmo de consenso para resolver conflitos
        """
        neighbors = self.nodes
        longest_chain = None

        max_length = len(self.chain)

        for node in neighbors:
            response = requests.get(f'http://{node}/chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                if length > max_length and self.is_valid_chain(chain):
                    max_length = length
                    longest_chain = chain

        if longest_chain:
            self.chain = longest_chain
            return True

        return False

    def add_block(self, proof, previous_hash):
        """
        Adiciona um novo bloco à blockchain
        """
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.pending_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }

        # Limpa as transações pendentes
        self.pending_transactions = []

        self.chain.append(block)
        return block

    def create_transaction(self, sender, recipient, amount):
        """
        Cria uma nova transação para ser incluída no próximo bloco
        """
        self.pending_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })

        return self.last_block['index'] + 1

    def calculate_proof(self, last_proof):
        """
        Algoritmo de prova de trabalho simplificado
        """
        proof = 0
        while not self.is_valid_proof(last_proof, proof):
            proof += 1

        return proof

    @staticmethod
    def hash(block):
        """
        Cria um hash SHA-256 do bloco
        """
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def is_valid_chain(self, chain):
        """
        Verifica se a blockchain fornecida é válida
        """
        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            last_block_hash = self.hash(last_block)

            if block['previous_hash'] != last_block_hash:
                return False

            if not self.is_valid_proof(last_block['proof'], block['proof']):
                return False

            last_block = block
            current_index += 1

        return True

    @staticmethod
    def is_valid_proof(last_proof, proof):
        """
        Valida a prova de trabalho
        """
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "1234"

    @property
    def last_block(self):
        return self.chain[-1]


# Instancia o servidor Flask
app = Flask(__name__)

# Gera um identificador único para este nó
node_id = str(uuid4()).replace('-', '')

# Instancia a blockchain
blockchain = Chain()


@app.route('/mine', methods=['GET'])
def mine():
    last_block = blockchain.last_block
    proof = blockchain.calculate_proof(last_block['proof'])

    blockchain.create_transaction(
        sender="0",
        recipient=node_id,
        amount=1,
    )

    previous_hash = blockchain.hash(last_block)
    block = blockchain.add_block(proof, previous_hash)

    response = {
        'message': "Novo bloco criado",
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
    if not all(k in values for k in required):
        return 'Campos ausentes', 400

    index = blockchain.create_transaction(values['sender'], values['recipient'], values['amount'])

    response = {'message': f'Transação será adicionada ao bloco {index}'}
    return jsonify(response), 201


@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
