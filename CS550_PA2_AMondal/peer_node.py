import socket
import sys
import threading
import os
import hashlib
#from time 
import time 

CHUNK_SIZE = 64 * 1024  # 64KB
INDEXING_SERVER = ("127.0.0.1", 1313)
PEER_NODE_PORT = 12349


class PeerNode:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.folder = f"peer_{host}_{port}"
        self.create_folder()
        #self.register_files()
        self.start_server()

    def create_folder(self):
        if not os.path.exists(self.folder):
            os.makedirs(self.folder)
    
    def user_interface(self):
        while True:
            print("\nOptions:")
            print("1. List local files")
            print("2. Register files with the Central Index")
            print("3. Query a file")
            print("4. Exit")
            choice = input("\nEnter your choice: ")

            if choice == "1":
                self.list_local_files()
            elif choice == "2":
                self.register_files()
            elif choice == "3":
                file_name = input("Enter the name of the file you want to query: ")
                self.request_file(file_name)
            elif choice == "4":
                print("Exiting...")
                break
            else:
                print("Invalid choice. Please try again.")


    def register_files(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(INDEXING_SERVER)
            files_to_register = []
            for file in os.listdir(self.folder):
                file_path = os.path.join(self.folder, file)
                file_size = os.path.getsize(file_path)
                files_to_register.append(f"{file}:{file_size}")
            
            if not files_to_register:
                print("No files to register.")
                return
            
            file_count = len(files_to_register)
            file_list_str = ';'.join(files_to_register)
            register_request = f"REGISTER:{self.host}:{self.port};{file_count};{file_list_str}"
            s.send(register_request.encode())
            response = s.recv(1024).decode()
            print(f"Response for file registration: {response}")

    def start_server(self):
        try:
            server_thread = threading.Thread(target=self.run_server)
            server_thread.start()
        except OSError as e:
            if e.winerror == 10048:
                print(f"ERROR: There is another active peer node on port {self.port}")
            else:
                print(f"An unexpected error occurred: {e}")
            sys.exit(1)

    def run_server(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.host, self.port))
            s.listen()
            print(f"Peer Node listening on {self.host}:{self.port}")
            while True:
                conn, addr = s.accept()
                client_thread = threading.Thread(target=self.handle_client, args=(conn, addr))
                client_thread.start()

    def handle_client(self, conn, addr):
        data = conn.recv(1024).decode()
        if data:
            request = data.split(':')
            if request[0] == "GET_CHUNK":
                file_name = request[1]
                start_offset = int(request[2])
                file_path = os.path.join(self.folder, file_name)
                with open(file_path, "rb") as f:
                    f.seek(start_offset)
                    chunk = f.read(CHUNK_SIZE)
                conn.send(chunk)
        conn.close()

    def request_file(self, file_name):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(INDEXING_SERVER)
            s.send(f"QUERY:{file_name}".encode())
            response = s.recv(1024).decode()
            print(f"Response for file query: {response}")
            if response.startswith("FOUND"):
                response_parts = response.split(';')
                file_size = int(response_parts[0].split(':')[1])
                print(f"file size: {file_size}")
                number_of_nodes = response_parts[1]
                print(f"number of nodes with the same file {number_of_nodes}")
                # print(f"peer nodes str: {peer_nodes_str}")
                # Split the peer_nodes_str by comma to get individual peer nodes
                #peer_nodes_list = peer_nodes_str.split(',')
                # Create a list of tuples with IP addresses and port numbers
                peer_nodes_str = response_parts[2]
                print(peer_nodes_str)
                peer_nodes_list = peer_nodes_str.split(',')
                # Create a list of tuples with IP addresses and port numbers
                peer_nodes = [(node.split(':')[0], int(node.split(':')[1])) for node in peer_nodes_list]
                #peer_nodes = [(node.split(':')[0], int(node.split(':')[1])) for node in peer_nodes_str]
                print(f"Peer nodes: {peer_nodes}")

                start_time = time.time()
                self.download_file(file_name, file_size, peer_nodes)
                end_time = time.time()
                elapsed_time = end_time - start_time
                print(f"Time taken to download the file: {elapsed_time} seconds")
            else:
                print("File not found.")
    
    def list_local_files(self):
        files = os.listdir(self.folder)
        if not files:
            print("No files found.")
        else:
            print("\nLocal files:")
            for file in files:
                file_path = os.path.join(self.folder, file)
                file_size = os.path.getsize(file_path)
                print(f"{file} - {file_size} bytes")
            
    def download_file(self, file_name, file_size, peer_nodes):
        file_path = os.path.join(self.folder, file_name)
        num_chunks = -(-file_size // CHUNK_SIZE)
        chunk_data = [b""] * num_chunks
        output = []

        def download_chunk(node, chunk_idx):
            nonlocal output
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(node)
                s.send(f"GET_CHUNK:{file_name}:{chunk_idx * CHUNK_SIZE}".encode())
                chunk_data[chunk_idx] = s.recv(CHUNK_SIZE)
            output.append(f"Chunk {chunk_idx + 1} from {node} at {time.time()}")

        # Download chunks from multiple peer nodes in a round-robin fashion
        peer_nodes_list = list(peer_nodes)
        threads = []
        for i in range(num_chunks):
            node = peer_nodes_list[i % len(peer_nodes_list)]
            thread = threading.Thread(target=download_chunk, args=(node, i))
            thread.start()
            threads.append(thread)

        # Wait for all threads to finish
        for thread in threads:
            thread.join()

        # Write downloaded chunks to file
        with open(file_path, "wb") as f:
            for chunk in chunk_data:
                f.write(chunk)

        # Verify file integrity
        if self.check_file_integrity(file_path, file_size):
            print(f"File {file_name} downloaded successfully.")
            # Update file information with the indexing server
            self.register_files()
        else:
            print("File integrity check failed. Please try again.")
            os.remove(file_path)

        # Print the output
        for entry in output:
            print(entry)



    def check_file_integrity(self, file_path, original_size):
        file_size = os.path.getsize(file_path)
        return file_size == original_size
    
    def send_handshake(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(INDEXING_SERVER)
            s.send(f"HANDSHAKE:{self.host}:{self.port}".encode())
            response = s.recv(1024).decode()
            print(f"Response from CI received, temporary port assigned {response}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    else:
        print("You have not entered a port number, so it will be set to the default one of " + str(PEER_NODE_PORT) + " . Next time if you wish to start multiple ports, enter the port number you wish to listen on.")
        port = PEER_NODE_PORT

    peer_node = PeerNode("127.0.0.1", port)
    time.sleep(2)
    peer_node.send_handshake()
    peer_node.user_interface()
    # Request file example: 
    #peer_node.request_file("3.txt")

