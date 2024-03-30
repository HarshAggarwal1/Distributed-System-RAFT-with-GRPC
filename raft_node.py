import grpc
from concurrent import futures
import time
import datetime
import random

import raft_pb2
import raft_pb2_grpc

from raft_storage import RaftStorage

class RaftNode(raft_pb2_grpc.RaftServiceServicer):
    def __init__(self, node_id, my_address, peer_addresses):
        # Node information
        self.my_address = my_address
        self.node_id = node_id
        self.peer_addresses = peer_addresses
        self.temp_x = 0
        
        # Node state
        self.state = 'FOLLOWER'
        self.vote_count = 0
        self.current_term = 0

        # Leader information
        self.voted_for = ""
        self.leader_id = ""
        
        # Timeout and lease information
        self.lease_duration = 20 # seconds
        self.timeout = int(random.uniform(15, 20))
        # ====
        self.old_lease = 0
        self.next_lease = 0
        self.next_timeout = int(time.time()) + self.timeout
        
        # Storage
        self.commit_index = 0
        self.last_applied = 0
        self.logs = []
        self.metadata = {}
        self.dump = []
        
        self.raft_storage = RaftStorage(self.node_id)
        
        
    def start_election(self):
        
        if self.state != 'CANDIDATE':
            return
        
        self.current_term += 1
        # print(f"{datetime.datetime.now()} - Node {self.node_id} starting election for term {self.current_term}")
        self.raft_storage.save_dump_info(f"{datetime.datetime.now()} - Node {self.node_id} starting election for term {self.current_term}")
        
        self.voted_for = str(self.node_id)
        self.vote_count = 1
        
        request = raft_pb2.RequestVoteRequest(
            term=self.current_term,
            candidate_id=str(self.node_id),
            last_log_index=len(self.logs) - 1,
            last_log_term=self.logs[-1].term if self.logs else 0
        )
        
        for peer in self.peer_addresses:
            if peer != self.my_address:
                try:
                    with grpc.insecure_channel(peer) as channel:
                        stub = raft_pb2_grpc.RaftServiceStub(channel)
                        response = stub.RequestVote(request)
                        
                        if response.term > self.current_term:
                            self.state = 'FOLLOWER'
                            self.current_term = response.term
                            self.voted_for = peer
                            self.leader_id = response.leader_id
                            self.vote_count = 0
                            self.next_lease = 0
                            self.next_timeout = int(time.time()) + self.timeout
                            self.raft_storage.save_metadata(self.commit_index, self.current_term, self.voted_for, self.temp_x)
                            return
                        
                        if response.vote_granted:
                            self.vote_count += 1
                            
                        if self.vote_count > len(self.peer_addresses) // 2:
                            # print(f"{datetime.datetime.now()} - Node {self.node_id} won election for term {self.current_term}")
                            self.raft_storage.save_dump_info(f"{datetime.datetime.now()} - Node {self.node_id} won election for term {self.current_term}")
                            self.state = 'LEADER'
                            self.leader_id = self.node_id
                            self.next_lease = int(time.time()) + self.lease_duration
                            self.old_lease = 0
                            self.raft_storage.save_metadata(self.commit_index, self.current_term, None, self.temp_x)
                            self.send_heartbeat()
                            return
                except grpc.RpcError as e:
                    # print(e)
                    # print(f"Error sending RequestVote to {peer}")
                    self.raft_storage.save_dump_info(f"Error sending RequestVote to {peer}")
    
    
    def RequestVote(self, request, context):
        # print(f"{datetime.datetime.now()} - Node {self.node_id} received RequestVote from {request.candidate_id} for term {request.term}")
        self.raft_storage.save_dump_info(f"{datetime.datetime.now()} - Node {self.node_id} received RequestVote from {request.candidate_id} for term {request.term}")
        
        if request.term < self.current_term:
            self.raft_storage.dump_file.write(f"{datetime.datetime.now()} - Node {self.node_id} - {request.term} < {self.current_term}\n")
            return raft_pb2.RequestVoteResponse(term=self.current_term, vote_granted=False, leader_id=self.leader_id)
        else:
            self.current_term = request.term
            self.voted_for = request.candidate_id
            self.state = 'FOLLOWER'
            self.next_election_time = int(time.time()) + self.timeout
            self.vote_count = 0
            self.old_lease = int(time.time()) + self.lease_duration
            self.leader_id = request.candidate_id
            self.raft_storage.save_metadata(self.commit_index, self.current_term, self.voted_for, self.temp_x)
            self.raft_storage.save_dump_info(f"{datetime.datetime.now()} - Node {self.node_id} voted for {request.candidate_id} for term {request.term}")
            return raft_pb2.RequestVoteResponse(term=self.current_term, vote_granted=True)
    
    def send_heartbeat(self):
        if self.state != 'LEADER':
            return
        
        # print(f"{datetime.datetime.now()} - Node {self.node_id} sending heartbeat")
        self.raft_storage.save_dump_info(f"{datetime.datetime.now()} - Node {self.node_id} sending heartbeat")
        
        for peer in self.peer_addresses:
            if peer != self.my_address:
                try:
                    with grpc.insecure_channel(peer) as channel:
                        stub = raft_pb2_grpc.RaftServiceStub(channel)
                        request = raft_pb2.AppendEntryRequest(
                            term = self.current_term,
                            leader_id = str(self.node_id),
                            entry = [raft_pb2.LogEntry(term=self.current_term, key='heartbeat', value='No-OP')],
                            type = 0
                        )
                        response = stub.AppendEntry(request)
                        if response.success:    
                            if response.term > self.current_term:
                                self.state = 'FOLLOWER'
                                self.current_term = response.term
                                self.voted_for = peer
                                self.leader_id = response.leader_id
                                self.vote_count = 0
                                self.next_lease = 0
                                self.next_timeout = int(time.time()) + self.timeout
                                self.raft_storage.save_metadata(self.commit_index, self.current_term, self.voted_for, self.temp_x)
                                return
                            else:
                                self.next_lease = int(time.time()) + self.lease_duration
                                self.next_timeout = int(time.time()) + self.timeout
                except grpc.RpcError:
                    # print(f"Error sending HeartBeat to {peer}")
                    self.raft_storage.save_dump_info(f"Error sending HeartBeat to {peer}")
                    
    def AppendEntry(self, request, context):
        if request.term < self.current_term:
            return raft_pb2.AppendEntryResponse(term=self.current_term, success=True, leader_id=self.leader_id)
        else:
            self.old_lease = int(time.time()) + self.lease_duration
            self.next_timeout = int(time.time()) + self.timeout
            if request.type == 0:
                self.raft_storage.append_log_entry(f"{datetime.datetime.now()} - NO-OP")
                # print(f"{datetime.datetime.now()} - Node {self.node_id} received heartbeat from {request.leader_id}")
                self.raft_storage.save_dump_info(f"{datetime.datetime.now()} - Node {self.node_id} received heartbeat from {request.leader_id}")
                self.current_term = request.term
                self.raft_storage.save_metadata(self.commit_index, self.current_term, self.voted_for, self.temp_x)
                return raft_pb2.AppendEntryResponse(term=self.current_term, success=True, leader_id=self.leader_id)
            elif request.type == 1:
                # print(f"{datetime.datetime.now()} - Node {self.node_id} received  PRE FINAL SET request from {request.leader_id}")
                self.raft_storage.save_dump_info(f"{datetime.datetime.now()} - Node {self.node_id} received  PRE FINAL SET request from {request.leader_id}")
                self.temp_x = request.entry[0].value
                
            elif request.type == 2:
                # print(f"{datetime.datetime.now()} - Node {self.node_id} received FINAL SET request from {request.leader_id}")
                self.raft_storage.append_log_entry(f"{datetime.datetime.now()} - SET x: {self.temp_x}")
                self.raft_storage.save_dump_info(f"{datetime.datetime.now()} - Node {self.node_id} received FINAL SET request from {request.leader_id}")
                self.replication_handler(request.prev_log_index, request.entry, request.leader_commit)
                
            self.raft_storage.save_metadata(self.commit_index, self.current_term, self.voted_for, self.temp_x)
                           
            # print(f"{datetime.datetime.now()} - Node {self.node_id} logs: {self.logs}")
            return raft_pb2.AppendEntryResponse(term=self.current_term, success=True, leader_id=self.leader_id)
        
    def replication_handler(self, prev_log_index, entry, leader_commit):
        if prev_log_index == 0:
            self.logs = entry
        else:
            ind = min(prev_log_index - 1, len(self.logs) - 1)
            found = -1
            while ind >= 0:
                if self.logs[ind].term == entry[0].term:
                    found = ind
                    break
                # print(f"{datetime.datetime.now()} - Node {self.node_id} - {self.logs[ind].term} != {entry[0].term}")
                self.raft_storage.save_dump_info(f"{datetime.datetime.now()} - Node {self.node_id} - {self.logs[ind].term} != {entry[0].term}")
                ind -= 1
            
            if found == -1:
                self.logs = entry
            else:    
                self.logs = self.logs[:found + 1]
                i = found + 1
                while i < len(entry):
                    self.logs.append(entry[i])
                    i += 1
        
        if leader_commit > self.commit_index:
            self.commit_index = min(leader_commit, len(self.logs) - 1)
            
    
    def ServeClient(self, request, context):
        if self.state != 'LEADER' or self.old_lease > int(time.time()):
            return raft_pb2.ServeClientResponse(success=False, leader_id=str(self.leader_id))
        
        # print(f"{datetime.datetime.now()} - Node {self.node_id} serving client: {request.address}")
        self.raft_storage.save_dump_info(f"{datetime.datetime.now()} - Node {self.node_id} serving client: {request.address}")
        
        type = request.type
        
        if type == 'GET':
            key = request.key
            value = self.metadata.get(key)
            self.raft_storage.save_metadata(self.commit_index, self.current_term, self.voted_for, self.temp_x)
            self.raft_storage.append_log_entry(f"{datetime.datetime.now()} - GET x")
            return raft_pb2.ServeClientResponse(success=True, data=str(value), leader_id=str(self.node_id))
        else:
            key = request.key
            value = request.value
            self.temp_x = value
            
            # print(key, value)
            
            count = 1
            
            for peer in self.peer_addresses:
                if peer != self.my_address:
                    try:
                        with grpc.insecure_channel(peer) as channel:
                            stub = raft_pb2_grpc.RaftServiceStub(channel)
                            request = raft_pb2.AppendEntryRequest(
                                term = self.current_term,
                                leader_id = str(self.node_id),
                                entry = [raft_pb2.LogEntry(term=self.current_term, key=key, value=value)],
                                type = 1
                            )
                            response = stub.AppendEntry(request)
                            if response.success:
                                self.next_lease = int(time.time()) + self.lease_duration
                                self.next_timeout = int(time.time()) + self.timeout
                                count += 1
                    except grpc.RpcError:
                        # print(f"Error sending AppendEntries to {peer}")
                        self.raft_storage.save_dump_info(f"Error sending AppendEntries to {peer}")
            
            if count > len(self.peer_addresses) // 2:
                # print(f"{datetime.datetime.now()} - Node {self.node_id} SET request successful")
                self.raft_storage.save_dump_info(f"{datetime.datetime.now()} - Node {self.node_id} SET request successful")
                self.metadata[key] = value
                self.commit_index += 1
                self.logs.append(raft_pb2.LogEntry(term=self.current_term, key=key, value=value))
                self.raft_storage.append_log_entry(f"{datetime.datetime.now()} - SET x: {value}")
                # print(f"{datetime.datetime.now()} - Node {self.node_id} FINAL SET request successful") 
                for peer in self.peer_addresses:
                    if peer != self.my_address:
                        try:
                            with grpc.insecure_channel(peer) as channel:
                                stub = raft_pb2_grpc.RaftServiceStub(channel)                                
                                request = raft_pb2.AppendEntryRequest(
                                    term = self.current_term,
                                    leader_id = str(self.node_id),
                                    entry = self.logs,
                                    type = 2,
                                    prev_log_index = len(self.logs) - 1,
                                    leader_commit = self.commit_index
                                )
                                response = stub.AppendEntry(request)
                                if response.success:
                                    self.next_lease = int(time.time()) + self.lease_duration
                                    self.next_timeout = int(time.time()) + self.timeout
                        except grpc.RpcError:
                            # print(f"Error sending AppendEntries to {peer}")
                            self.raft_storage.save_dump_info(f"Error sending AppendEntries to {peer}")
                
                self.raft_storage.save_metadata(self.commit_index, self.current_term, self.voted_for, self.temp_x)
                
                # print(f"{datetime.datetime.now()} - Node {self.node_id} logs: {self.logs}")
                self.raft_storage.save_dump_info(f"{datetime.datetime.now()} - Node {self.node_id} logs: {self.logs}")
                return raft_pb2.ServeClientResponse(success=True)
            
            else :
                # print(f"{datetime.datetime.now()} - Node {self.node_id} SET request failed")
                return raft_pb2.ServeClientResponse(success=False)
            
        
        

def run(node):
    print(f"{datetime.datetime.now()} - Node {node.node_id} started")
    print(f"{datetime.datetime.now()} - Peer Addresses: {node.peer_addresses}")
    print(f"{datetime.datetime.now()} - My Address: {node.my_address}")
    print(f"{datetime.datetime.now()} - Election Timeout: {node.timeout}")
    print(f"{datetime.datetime.now()} - Node {node.node_id} - Current Term: {node.current_term}")
    print("============================================================") 
    
    node.temp_x = node.raft_storage.load_metadata()[3]
    node.current_term = node.raft_storage.load_metadata()[1]
    node.voted_for = node.raft_storage.load_metadata()[2]
    node.commit_index = node.raft_storage.load_metadata()[0]
    
    
    while True:
        if node.state == 'FOLLOWER' and int(time.time()) > node.next_timeout:
            node.voted_for = None
            node.leader_id = None
            node.vote_count = 0
            node.next_timeout = int(time.time()) + node.timeout
            node.state = 'CANDIDATE'
            node.start_election()
        elif node.state == 'CANDIDATE':
            node.start_election()
        elif node.state == 'LEADER' and int(time.time()) > node.next_lease:
            node.next_lease = 0
            node.state = 'FOLLOWER'
        elif node.state == 'LEADER':
            node.send_heartbeat()
        time.sleep(1)


def serve():
    print("Starting Raft Node")
    print("============================================================")
    
    try:
        node_id = int(input("Enter Node ID: "))
        my_address = input("Enter my address: ")
        peer_addresses = ["localhost:50051", "localhost:50052"]
        
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        node = RaftNode(node_id, my_address, peer_addresses)
        raft_pb2_grpc.add_RaftServiceServicer_to_server(node, server)
        server.add_insecure_port(my_address)
        server.start()
        
        try:
            run(node)
        except KeyboardInterrupt:
            server.stop(0)
    except Exception as e:
        # print(e)
        print(f"{datetime.datetime.now()} - Error Occured starting Raft Node")
    
    
if __name__ == "__main__":
    serve()