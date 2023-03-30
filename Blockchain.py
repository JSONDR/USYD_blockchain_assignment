import hashlib
import json
from time import time
import datetime

class Blockchain():
    def  __init__(self):
        self.blockchain = []
        self.pool = []
        self.poolLimit = 5

    def newBlock(self, proof, previousHash = None):
        block = {
            'index': len(self.blockchain) + 1,
            'timestamp': str(datetime.datetime.now()),
            'transaction': self.pool,
            'proof': proof,
            'previousHash': previousHash or self.calculateHash(self.blockchain[-1]),
            'currentHash': self.currentHash(self.pool)
        }
        self.pool = []
        self.blockchain.append(block)
    
    def lastBlock(self):
        return self.blockchain[-1]

    def calculateHash(self, block):
        blockObject = json.dumps(block, sort_keys=True)
        blockString = blockObject.encode()
        rawHash = hashlib.sha256(blockString)
        hexHash = rawHash.hexdigest()
        return hexHash
    
    def addTransaction(self, transaction):
        if len(self.pool) < self.poolLimit:
            self.pool.append(transaction)
        lastBlock = self.lastBlock()
        return lastBlock['index'] + 1
        
    def currentHash(self, pool):
        if(len(self.blockchain) == 0):
            #genesis block
            return hashlib.sha256("The Times 03/Jan/2009 Chancellor on brink of second bailout for banks.".encode()).hexdigest()
        currentTransactions = ""
        previousHash = self.calculateHash(self.lastBlock())
        currentTransactions += previousHash
        for transaction in pool:
            currentTransactions += transaction
        currentTransactions += str(self.lastBlock()['proof'])
        return hashlib.sha256(currentTransactions.encode()).hexdigest()
    
    def previousHash(self):
        return self.blockchain[-1]['currentHash']