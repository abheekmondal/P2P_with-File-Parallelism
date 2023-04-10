import socket
import pickle
import threading

class CentralIndexingServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.active_nodes = {}
        self.file_data = "file_data.pickle"
        self.load_file_data()

    def load_file_data(self):
        try:
            with open(self.file_data, "rb") as f:
                self.active_nodes = pickle.load(f)
        except FileNotFoundError:
            self.active_nodes = {}
            self.save_file_data()  # Save the empty dictionary as a new pickle file

    def print_pickle_file(file_name):
        try:
            with open(file_name, 'rb') as f:
                data = pickle.load(f)
            print(data)
        except FileNotFoundError:
            print(f"File '{file_name}' not found.")
        except Exception as e:
            print(f"An error occurred while reading the file: {e}")

    def save_file_data(self):
        with open(self.file_data, "wb") as f:
            pickle.dump(self.active_nodes, f)

    def handle_client(self, conn, addr):
        data = conn.recv(1024).decode()
        print(f"Received data from client: {data}")
        if data:
            request = data.split(':')
            if request[0] == "HANDSHAKE":
                print(f"Request from {addr[1]}, reply sent.")
                conn.send(f"CONFIRM_HANDSHAKE:{addr[1]}".encode())
            elif request[0] == "QUERY":
                file_name = request[1]
                if file_name in self.active_nodes:
                    file_size = self.active_nodes[file_name]["size"]
                    peer_nodes = [node for node in self.active_nodes[file_name]["nodes"]]
                    number_of_nodes = len(peer_nodes)
                    response = f"FOUND:{file_size};{number_of_nodes};{','.join(peer_nodes)}"
                else:
                    response = "NOT_FOUND"
                print(f"Sending response to client: {response}")
                conn.send(response.encode())
            elif request[0] == "REGISTER":
                request = data.strip().split(';')
                #print(request)
                #print(request[1].split(':'))
                host, port = request[0].split(':')[1], request[0].split(':')[2]
                #print (host,port)
                node_address = f"{host}:{port}"
                #print(node_address)
                file_count = int(request[1])
                #print(file_count)
                x = 0
                file_list = [request[2+x] for x in range(file_count)]
                file_list_str = ';'.join(file_list)
                #print(file_list_str)
                #print("This is it" + file_list_str)
                #print(f"Processing: {file_info}")
                for file_info in file_list_str.split(';'):
                    file_name, file_size = file_info.split(':')
                    #print(file_name)
                    #print(file_size)
                    #node_address = f"{host}:{port}"
                    #print (host,port)
                    if file_name not in self.active_nodes:
                        self.active_nodes[file_name] = {"size": file_size, "nodes": set()}
                    self.active_nodes[file_name]["nodes"].add(node_address)
                print(self.active_nodes)
                self.save_file_data()
                #result = self.save_file_data()
                # Send the response to the client
                response = f"{file_count} Files have been registered"
                conn.send(response.encode())
            elif request[0] == "UNREGISTER":
                file_name = request[1]
                node_address = f"{addr[0]}:{addr[1]}"
                if file_name in self.active_nodes:
                    self.active_nodes[file_name]["nodes"].discard(node_address)
                    if not self.active_nodes[file_name]["nodes"]:
                        del self.active_nodes[file_name]
                    self.save_file_data()
                conn.send("UNREGISTERED".encode())
        conn.close()


    def start(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.host, self.port))
            s.listen()
            print(f"Central Indexing Server listening on {self.host}:{self.port}")
            while True:
                conn, addr = s.accept()
                print(f"Connected to {addr}")
                client_thread = threading.Thread(target=self.handle_client, args=(conn, addr))
                client_thread.start()

if __name__ == "__main__":
    central_indexing_server = CentralIndexingServer("127.0.0.1", 1313)
    central_indexing_server.start()
