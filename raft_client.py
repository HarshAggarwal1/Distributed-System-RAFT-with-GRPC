import grpc
import raft_pb2
import raft_pb2_grpc
import time
import datetime

class RaftClient:
    def __init__(self, address):
        self.address = address
        self.leader = None
        self.addresses = ["localhost:50051", "localhost:50052", "localhost:50053", "localhost:50054", "localhost:50055"]

    def main(self):
        print(f"{datetime.datetime.now()} - Client started at {self.address}")
        print("===============================================================")
        
        for addr in self.addresses:
            try:
                channel = grpc.insecure_channel(addr)
                stub = raft_pb2_grpc.RaftServiceStub(channel)
                request = raft_pb2.ServeClientRequest(
                    address=self.address,
                    type='GET'
                )
                response = stub.ServeClient(request)
                
                if response.success:
                    self.leader = self.addresses[int(response.leader_id)]
                    print(f"{datetime.datetime.now()} - Leader is {self.leader}")
                    break
                
            except Exception as e:
                # print(e)
                print(f"{datetime.datetime.now()} - Some error occured, trying again")
        
        while True and self.leader is not None:
            type = int(input("Enter the type of request (get[1], set[2]): "))
            if type == 1:
                type = "GET"
            elif type == 2:
                type = "SET"
            
            key = "x"
            value = ""
            
            if type == "SET":
                value = input("Enter the value, else leave blank: ")
                
            with grpc.insecure_channel(self.leader) as channel:
                stub = raft_pb2_grpc.RaftServiceStub(channel)
                request = raft_pb2.ServeClientRequest(
                    address=address,
                    type=type,
                    key=key,
                    value=value
                )
                response = stub.ServeClient(request)
                if type == "GET":
                    print(f"{datetime.datetime.now()} - {response.data}")
                print("===============================================================")
                time.sleep(2)
    
    


if __name__ == "__main__":
    address = str(input("Enter the address of the client: "))
    client = RaftClient(address)
    client.main()
    