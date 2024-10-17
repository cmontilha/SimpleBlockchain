import hashlib
import json
from time import time

class Blockchain:
    def __init__(self):
        self.chain = []
        self.current_transactions = []

        # Cria o bloco gênesis
        self.new_block(previous_hash='1', proof=100)

    def new_block(self, proof, previous_hash=None):
        """
        Cria um novo bloco na blockchain
        :param proof: <int> A prova dada pelo algoritmo de Proof of Work
        :param previous_hash: (Opcional) <str> Hash do bloco anterior
        :return: <dict> Novo Bloco
        """
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }

        # Reseta a lista de transações atuais
        self.current_transactions = []

        self.chain.append(block)
        return block

    def new_transaction(self, sender, recipient, amount):
        """
        Cria uma nova transação para ser incluída no próximo bloco minerado
        :param sender: <str> Endereço do remetente
        :param recipient: <str> Endereço do destinatário
        :param amount: <int> Quantidade
        :return: <int> O índice do bloco que conterá a transação
        """
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })

        return self.last_block['index'] + 1

    @staticmethod
    def hash(block):
        """
        Cria um hash SHA-256 de um bloco
        :param block: <dict> Bloco
        :return: <str> Hash do bloco
        """
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        # Retorna o último bloco da cadeia
        return self.chain[-1]

    def new_transaction(self, sender, recipient, amount):
        """
        Cria uma nova transação para ser incluída no próximo bloco minerado
        :param sender: <str> Endereço do remetente
        :param recipient: <str> Endereço do destinatário
        :param amount: <int> Quantidade
        :return: <int> O índice do bloco que conterá a transação
        """
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })

        return self.last_block['index'] + 1

    @staticmethod
    def hash(block):
        """
        Cria um hash SHA-256 de um bloco
        :param block: <dict> Bloco
        :return: <str> Hash do bloco
        """
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        # Retorna o último bloco da cadeia
        return self.chain[-1]

    def proof_of_work(self, last_proof):
        """
        Algoritmo simples de Proof of Work:
        - Encontre um número p' tal que hash(pp') contenha 4 zeros à esquerda, onde p é a prova anterior
        :param last_proof: <int> Prova anterior
        :return: <int> Nova prova
        """
        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1

        return proof

    @staticmethod
    def valid_proof(last_proof, proof):
        """
        Valida a prova: hash(last_proof, proof) deve conter 4 zeros à esquerda
        :param last_proof: <int> Prova anterior
        :param proof: <int> Prova atual
        :return: <bool> Verdadeiro se correto, Falso se não
        """
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"



from flask import Flask, jsonify, request
from uuid import uuid4

# Instancia o Flask
app = Flask(__name__)

# Gera um endereço único para este nó
node_identifier = str(uuid4()).replace('-', '')

# Instancia a Blockchain
blockchain = Blockchain()

@app.route('/mine', methods=['GET'])
def mine():
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)

    # Recompensa por encontrar a prova
    blockchain.new_transaction(
        sender="0",
        recipient=node_identifier,
        amount=1,
    )

    # Cria o novo bloco
    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)

    response = {
        'message': "Novo Bloco Forjado",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    return jsonify(response), 200

@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()

    # Verifica se os campos obrigatórios estão presentes
    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Valores faltando', 400

    # Cria uma nova transação
    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])

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
