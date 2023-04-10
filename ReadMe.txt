README for peer_node.py

This is a simple peer-to-peer (P2P) file sharing system implemented in Python. The system consists of peer nodes that share files with each other, and a central indexing server that maintains a registry of available files and their respective locations.

Features

    Register files with the Central Index
    Query files from the Central Index
    Download files from multiple peer nodes in parallel
    Verify file integrity after download
    Simple user interface to interact with the system
    Saves registered node data on to a pickle file

Dependencies

    Python 3.x

How to Run

Start the Central Indexing Server (not included in this code, please refer to the appropriate server code).
Start the PeerNode by running python peer_node.py [port], where [port] is the desired port number on which the PeerNode will listen. If no port number is provided, the default port 12349 will be used. If a new peer node port is specified, then the program will automatically create a new folder for it to use as its directory.
Follow the on-screen prompts to interact with the system.


README for central_index.py

This is a simple Central Indexing Server (CIS) for a distributed file sharing system. The CIS keeps track of file information and the active nodes (peers) that have the files. It facilitates file discovery and retrieval by responding to peer node requests for registering files, querying files, and unregistering files.
Features

    Register files from peer nodes
    Respond to file queries from peer nodes
    Unregister files upon request
    Maintain a persistent record of file information and active nodes
    Handle multiple clients using threading

Usage

To run the Central Indexing Server:

    Ensure that you have Python 3 installed on your system.
    Save the given code in a file named central_indexing_server.py.
    Open a terminal or command prompt and navigate to the directory where the central_indexing_server.py file is located.
    Run the script using the following command: python central_indexing_server.py.

The server will start listening on IP address 127.0.0.1 and port 1313.