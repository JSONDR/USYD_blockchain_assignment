from _thread import *
import threading
import time
import datetime
import socket
import _thread
import json 
from Blockchain import Blockchain
from Transaction import Transaction
import hashlib
import ast
import os

lock = threading.Lock()

IP = "127.0.0.1" # '' -> localhost
PORT_Server = 0

# this variable can be used in case of avoiding deadlock
counter = 0
cc = ""
ret_val = 0
# Shared resource between thread which sends hb, and server
blockchain = Blockchain()

class BlockchainServer():
    def __init__(self, *args):
        global blockchain
        self.args = args
        self.blockchain = blockchain
        blockchain.newBlock(previousHash="The Times 03/Jan/2009 Chancellor on brink of second bailout for banks.", proof=100)
    
    def check_proof_validity(self, previous_proof, new_proof):
        _input = (new_proof ** 2) - (previous_proof ** 2)  
        hexHash = self.calculateHash(_input)[:2]
        if(hexHash == "00"):
            return True
        return False
    
    def calculateHash(self, _input):
        rawHash = hashlib.sha256(str(_input).encode("utf-8"))
        hexHash = rawHash.hexdigest()
        return hexHash

    def broadcast_hb_to_peers(self):
        peers = self.args[1]
        start_time = time.time()
        while(True):
            end_time = time.time()
            if(end_time - start_time >= 5):
                start_time = time.time()
                for peer in peers:
                    port = peer[1]
                    try:
                        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                            s.connect((IP, port)) # Bind to the port
                            mess_data = bytes("hb", encoding= 'utf-8')
                            s.sendall(mess_data)
                            # get last block from peer
                            data_rev = s.recv(1024)
                            dataString = data_rev.decode('utf-8')
                            #get last block
                            block = None
                            try:
                                block = json.loads(dataString)
                            except Exception as e:
                                print(e)
                                continue
                            lock.acquire()
                            # if last block from peer has an index greater than local blockchain, then begin transmission of entire blockchain
                            if(block['index'] > self.blockchain.lastBlock()['index']):
                                self.blockchain = Blockchain()
                                mess_data = bytes("transmit blockchain", encoding= 'utf-8')
                                s.sendall(mess_data)
                                data_rev = s.recv(1024)
                                dataString = data_rev.decode('utf-8')
                                while(dataString != "hb finished"):
                                    block = None
                                    #There could be a different message broadcasted here
                                    try:
                                        block = json.loads(dataString)
                                        # Append block
                                        self.blockchain.blockchain.append(block)
                                        self.blockchain.pool = []
                                        mess_data = bytes("block ack", encoding= 'utf-8')
                                        s.sendall(mess_data)
                                    except Exception as e:
                                        print(e)
                                        continue
                                    data_rev = s.recv(1024)
                                    dataString = data_rev.decode('utf-8')
                            else:
                                mess_data = bytes("blockchain up to date", encoding= 'utf-8')
                                s.sendall(mess_data)
                            lock.release()
                            s.close()
                    except socket.error as e:
                        pass

    def broadcast_block_to_peers(self):
        peers = self.args[1]
        for peer in peers:
            port = peer[1]
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect((IP, port)) # Bind to the port
                    block = str(json.dumps(self.blockchain.lastBlock()))
                    mess_data = bytes("bb|" + block, encoding= 'utf-8')
                    s.sendall(mess_data)
                    s.close()
            except socket.error as e:
                pass

    def broadcast_tx_to_peers(self, transaction):
        peers = self.args[1]
        for peer in peers:
            port = peer[1]
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect((IP, port)) # Bind to the port
                    mess_data = bytes("bt|" + transaction, encoding= 'utf-8')
                    s.sendall(mess_data)
                    s.close()
            except socket.error as e:
                pass

    def serverHandler(self, c , addr):
        global cc
        global counter
        while(True):
            counter += 1
            # Parsing and processing data from client
            data_rev = c.recv(1024)
            dataString = data_rev.decode('utf-8')
            typeRequest = dataString[:2]

            clientData = ""
            # Handle tx request
            if typeRequest == 'tx':
                transaction = Transaction()
                transactionContent = transaction.validateTransaction(dataString)
                if transactionContent != None:
                    lock.acquire()
                    if(len(self.blockchain.pool) <= self.blockchain.poolLimit):
                        self.blockchain.addTransaction(transactionContent)
                        clientData = "Accepted"
                        self.broadcast_tx_to_peers(transactionContent)
                    else:
                        print("Did not add transction; otherwise pool limit would be exceeded")
                        clientData = "Rejected"
                    lock.release()
                else:
                    clientData = "Rejected"
            elif typeRequest == 'bb':
                block = dataString[4:-1]
                #print(block)
                block = "{" + block + "}"
                block = json.loads(block)
                #validate transactions 
                transactions = block['transaction']
                trans = Transaction()
                #assume block is valid
                is_valid_block = True
                for transaction in transactions:
                    if(trans.validateTransaction(transaction) == None):
                        print("Invalid transaction in peers block")
                        isValid = False
                        break
                #validate proof
                previous_proof = self.blockchain.lastBlock()['proof']
                new_proof = int(block['proof'])
                is_valid_proof = self.check_proof_validity(previous_proof, new_proof)
                if(is_valid_block == True and is_valid_proof == True):
                    #check if block with same index already exists
                    if(self.blockchain.lastBlock()['index'] < block['index']):
                        self.blockchain.blockchain.append(block)
                        self.blockchain.pool = []
                        #print("Proof and transactions are valid; and block with same index does not exist, so adding block to blockchain")
                #add block to blockchain
            # Handle pb request
            elif typeRequest == 'bt':
                tx = dataString[3:-1] + dataString[-1]
                trans = Transaction()
                if(len(self.blockchain.pool) <= self.blockchain.poolLimit):
                    tx = trans.validateTransaction(tx)
                    if(tx != None):
                        self.blockchain.pool.append(tx)
                    else:
                        print("A transaction received from peer invalid is invalid")
                else:
                    print("Pool size exceeded, not accepting transction")
            elif typeRequest == 'pb':
                lock.acquire()
                for block in self.blockchain.blockchain:
                    print("\n" + str(block))
                lock.release()
                continue
            elif typeRequest == 'gp':
                lock.acquire()
                clientData = str(self.blockchain.lastBlock()['proof'])
                lock.release()
            elif typeRequest == 'hb':
                lock.acquire()
                #send last block so that peer can check whether their blockchain is longer
                clientData = str(json.dumps(self.blockchain.lastBlock()))
                clientData = bytes(clientData, encoding='utf-8')
                c.sendall(clientData)
                data_rev = c.recv(1024)
                dataString = data_rev.decode('utf-8')
                if(dataString == "transmit blockchain"):
                    for block in self.blockchain.blockchain:                        
                        clientData = str(json.dumps(block))
                        clientData = bytes(clientData, encoding='utf-8')
                        c.sendall(clientData)
                        data_rev = c.recv(1024)
                        dataString = data_rev.decode('utf-8')
                        if(dataString != "block ack"):
                            print("There was an error while transmitting blockchain to a peer")
                            break
                lock.release()
                clientData = "hb finished"
                clientData = bytes(clientData, encoding='utf-8')
                c.sendall(clientData)
                continue
            elif typeRequest == 'up':
                #get new_proof from BlockchainMiner and previous_proof from blockchain
                new_proof = int(dataString.split("|")[1])
                lock.acquire()
                previous_proof = self.blockchain.lastBlock()['proof']
                is_valid = self.check_proof_validity(previous_proof, new_proof)
                if self.check_proof_validity(previous_proof, new_proof):
                    #notify other peers about new block
                    #return "Reward" to BlockchainMiner and broadcast proof to all peers
                    mess_data = bytes("Reward", encoding= 'utf-8')
                    self.blockchain.newBlock(new_proof)
                    #now broadcast new block to all peers
                    self.broadcast_block_to_peers()
                else:
                    #return "No reward"
                    mess_data = bytes("No reward", encoding= 'utf-8')
                lock.release()
                c.sendall(mess_data)
                continue
            # Handle cc request
            elif typeRequest == 'cc':
                cc = 'cc'
                clientData = "Connection closed!"

            clientData = bytes(clientData, encoding='utf-8')
            c.sendall(clientData)
            if typeRequest == 'cc':
                os._exit(1)
        c.close()
        return

    def run(self):
        global counter
        global cc
        global IP
        global PORT_Server
        global ret_val
        PORT_Server = self.args[0]
        _thread.start_new_thread(self.broadcast_hb_to_peers, ())
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                print("Blockchain Server start") 
                print("Blockchain Server host names: ", IP, "Port: ", PORT_Server)
                s.bind((IP, PORT_Server)) # Bind to the port
                s.listen(5)
                while True:
                    # to avoid deadlock, counter can be used here: if counter == 6 or cc = 'cc':
                    if cc == 'cc': 
                        exit()
                        break
                    c, addr = s.accept()
                    _thread.start_new_thread(self.serverHandler,(c, addr))
                s.close()
                return
        except socket.error as e:
            print(e)
            print("Can't connect to the Socket in Server")
