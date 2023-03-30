import sys
from _thread import *
import threading
import _thread
from Blockchain import Blockchain
from Transaction import Transaction
from BlockchainServer import BlockchainServer
from BlockchainClient import BlockchainClient
from BlockchainMiner import BlockchainMiner
import time

class BlockchainPeer():
    def __init__(self, *args):
        self.peer_id = args[0]
        self.port_no = args[1]
        self.peers = args[2]

    def run_server(self):
        server = BlockchainServer(self.port_no, self.peers)
        server.run()

    def run_client(self):
        client = BlockchainClient(self.port_no, self.peers)
        client.run()
    def run_miner(self):
        miner = BlockchainMiner(self.port_no)
        miner.run()
    def run(self):
        global cc
        _thread.start_new_thread(self.run_server, ())
        time.sleep(1)
        _thread.start_new_thread(self.run_client, ())
        time.sleep(1)
        _thread.start_new_thread(self.run_miner, ())
        time.sleep(1)
        while(1):
            pass

peer_id = sys.argv[1]
port_no = int(sys.argv[2])
peer_config = sys.argv[3]
config = open(peer_config, "r+")
lines = config.readlines()
lines = lines[ 1 : len(lines)]
peers = []
for line in lines:
    node_name = line.split(' ')[0]
    port_num = int(line.split(' ')[1].strip('\n'))
    peers.append((node_name, port_num))

peer = BlockchainPeer(peer_id, port_no, peers)
peer.run()