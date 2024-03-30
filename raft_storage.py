import os
import json

import raft_pb2

class RaftStorage():
    def __init__(self, node_id):
        self.node_id = node_id
        self.logs_directory = f"logs_node_{node_id}"
        
        if not os.path.exists(self.logs_directory):
            os.makedirs(self.logs_directory)
        
        self.logs_file = os.path.join(self.logs_directory, "logs.txt")
        self.metadata_file = os.path.join(self.logs_directory, "metadata.json")
        self.dump_file = os.path.join(self.logs_directory, "dump.txt")
        
    def load_metadata(self):
        if os.path.exists(self.metadata_file):
            file = open(self.metadata_file, 'r')
            metadata = json.load(file)
            # print(metadata)
            commit_index = metadata.get('commit_index', 0)
            current_term = metadata.get('current_term', 0)
            voted_for = metadata.get('voted_for', None)
            x_value = metadata.get('x_value', 0)
            
            return [commit_index, current_term, voted_for, x_value]
        else:
            return [0, 0, None, 0]
    
    def save_metadata(self, commit_index, current_term, voted_for, x_value):
        metadata = {
            'commit_index': commit_index,
            'current_term': current_term,
            'voted_for': voted_for,
            'x_value': x_value
        }
        
        with open(self.metadata_file, 'w') as file:
            json.dump(metadata, file)
    
    def append_log_entry(self, log_entry):
        with open(self.logs_file, 'a') as file:
            
            file.write(f"{log_entry} + '\n'")
    
    def read_logs(self):
        logs = []
        
        if os.path.exists(self.logs_file):
            with open(self.logs_file, 'r') as file:
                for line in file:
                    log_entry_dict = json.loads(line)
                    logs.append(raft_pb2.LogEntry(**log_entry_dict))
        
        return logs
    
    def save_dump_info(self, message):
        with open(self.dump_file, 'a') as file:
            file.write(message + '\n')
    
    
            