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