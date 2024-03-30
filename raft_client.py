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
    
    def find_leader(self):
        for addr in self.addresses:
            try:
                channel = grpc.insecure_channel(addr)
                stub = raft_pb2_grpc.RaftServiceStub(channel)
                request = raft_pb2.ServeClientRequest(
                    address=self.address,
                    type='GET'
                )
                response = stub.ServeClient(request)
                print(response)
                if response.success:
                    self.leader = self.addresses[int(response.leader_id)]
                    print(f"{datetime.datetime.now()} - Leader is {self.leader}")
                    break
                
            except Exception as e:
                # print(e)
                print(f"{datetime.datetime.now()} - Some error occured, trying again")

    def main(self):
        print(f"{datetime.datetime.now()} - Client started at {self.address}")
        self.find_leader()
        print("===============================================================")
        
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
                
            try:
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
            except grpc.RpcError:
                self.find_leader()
                    
            time.sleep(2)
    
    


if __name__ == "__main__":
    try:
        address = str(input("Enter the address of the client: "))
        client = RaftClient(address)
        client.main()
    except KeyboardInterrupt:
        print("\nExiting...")
        exit(0)
    