from _thread import *
import threading
import time
import socket
import _thread
import sys
import json
import hashlib

HOST = "127.0.0.1"
PORT_Server = 1993

class BlockchainClient():
    def __init__(self, *args):
        self.args = args    
    
    def calculateHash(self, input):
        rawHash = hashlib.sha256(input)
        hexHash = rawHash.hexdigest()
        return hexHash

    def check_proof_validity(self, previous_proof, new_proof):
        input = (new_proof ** 2) - (previous_proof ** 2)  
        hexHash = self.calculateHash(input)[:2]
        if(hexHash == "00"):
            return True
        return False

    def run(self):
        PORT_Server = self.args[0]
        print("Client running on port: {}".format(PORT_Server))
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s: # Create a socket object
                s.connect((HOST, PORT_Server))
                while(1):
                    # Parser for input command
                    commandContent = input("Please enter your command: ")
                    content = commandContent.split("|")
                    commandType = content[0]

                    # Process command
                    if commandType == 'tx':
                        if len(content) != 3:
                            print("Invalid transaction!")
                            continue
                        else:
                            requestContent = f"tx|{str(content[1])}|{str(content[2])}"
                            #print(requestContent)
                    elif commandType == 'pb':
                        if len(content) != 1:
                            print("Invalid arguments for pb request!")
                            continue
                        else:
                            requestContent = "pb"
                    elif commandType == 'cc':
                        if len(content) != 1:
                            print("Invalid arguments for cc request!")
                            continue
                        else:
                            requestContent = "cc"
                    else:
                        print("Please enter the supported request: ")
                        print("tx sender content -- [tx: command type of transaction] [sender of transaction] [content of transaction]")
                        print("pb -- [pb: command type of Print Blockchain]")
                        print("cc -- [cc: command type of Close Connection]")
                        continue
                    
                    # Create message for sending to Blockchain server
                    mess_data = bytes(requestContent, encoding= 'utf-8')
                    s.sendall(mess_data)
                s.close()   
        except:
            print("Can't connect to the Blockchain server in Client")