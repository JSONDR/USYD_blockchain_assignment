from _thread import *
import threading
import time
import socket
import _thread
import sys
import json
import hashlib
import time

#polls blockchain every 1 second
#if there is a new block, blockchain server sends new block to miner

HOST = "127.0.0.1" # '' -> localhost
PORT_Server = 1993

class BlockchainMiner():
    def __init__(self, *args):
        self.args = args
        self.block = None
        pass

    def process_block():
        pass

    def calculateHash(self, _input):
        rawHash = hashlib.sha256(str(_input).encode("utf-8"))
        hexHash = rawHash.hexdigest()
        return hexHash

    def proof_of_work(self, previous_proof):
        newProof = 0
        hexHash = ""
        start_time = time.time()
        end_time = time.time()
        while(start_time - end_time < 1):
            _input = (newProof ** 2) - (previous_proof ** 2)  
            hexHash = self.calculateHash(_input)[:2]
            if(hexHash == "00"):
                return newProof
            else:
                newProof += 1
            end_time = time.time()
        return -1

    def run(self):
        global PORT_Server
        PORT_Server = self.args[0]
        try: 
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s: # Create a socket object
                    s.connect((HOST, PORT_Server))
                    while(1):
                        requestContent = "gp"
                        # Create message for sending to Blockchain server
                        mess_data = bytes(requestContent, encoding='utf-8')
                        s.sendall(mess_data)

                        # Parse response from blockchain server
                        data_rev = s.recv(1024)
                        # Receive previous proof from Blockchain Server
                        response = data_rev.decode('utf-8')
                        if(response == "Reward" or response == "No reward"):
                            continue
                        if not data_rev:
                            print("Miner didn't get data")
                        else:
                            pass
                            #print("Miner received: {}".format(response))
                        #process block to extract previous proof
                        new_proof = self.proof_of_work(int(response))
                        if(new_proof != -1):
                            mess_data = bytes("up|" + str(new_proof), encoding= 'utf-8')
                            s.sendall(mess_data)
                            #wait for server to acknowledge
                            ack = s.recv(1024)
                        #time.sleep(1)
                    s.close()   
        except socket.error as e:
            print(e)
            print("Miner can't connect to the Blockchain server")