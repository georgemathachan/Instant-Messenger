import threading  # Import threading module to handle multiple client connections simultaneously
import socket  # Import socket module for network communication

host = '127.0.0.1' # Localhost - server runs on local machine
port = 55555  # Port number for server to listen on

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create TCP socket for IPv4
server.bind((host, port))  # Bind socket to the host and port
server.listen()  # Enable server to accept incoming connections
print(f"Server started on {host}:{port}")  # Display server start confirmation

clients = []  # List to store all connected client socket objects
nicknames = []  # List to store usernames corresponding to each client

def broadcast(message):  # Function to send message to all connected clients
    for client in clients:  # Iterate through all connected clients
        client.send(message)  # Send the message to each client

def handle(client):  # Function to handle individual client communication
    while True:  # Infinite loop to continuously receive messages
        try:  # Try block to catch connection errors
            message = client.recv(1024)  # Receive up to 1024 bytes from client
            broadcast(message)  # Broadcast received message to all clients
        except:  # Catch exceptions (client disconnection or errors)
            index = clients.index(client)  # Find the index of disconnected client
            clients.remove(client)  # Remove client from clients list
            client.close()  # Close the client socket connection
            nickname = nicknames[index]  # Get the nickname of disconnected client
            broadcast(f"{nickname} left the chat!".encode('utf-8'))  # Notify all clients of disconnection
            nicknames.remove(nickname)  # Remove nickname from nicknames list
            break  # Exit the loop for this client

def receive():  # Function to accept new client connections
    while True:  # Infinite loop to continuously accept new connections
        client, address = server.accept()  # Accept incoming connection and get client socket and address
        print(f"Connected with {str(address)}")  # Display connection information

        client.send('NICK'.encode('utf-8'))  # Request nickname from newly connected client
        nickname = client.recv(1024).decode('utf-8')  # Receive and decode the client's nickname
        nicknames.append(nickname)  # Add nickname to the nicknames list
        clients.append(client)  # Add client socket to clients list

        print(f"Username of the client is {nickname}")  # Display the client's username
        broadcast(f"{nickname} joined the chat!".encode('utf-8'))  # Notify all clients of new user
        client.send('Connected to the server!'.encode('utf-8'))  # Send confirmation message to new client

        thread = threading.Thread(target=handle, args=(client,))  # Create new thread to handle this client
        thread.start()  # Start the thread to begin handling client messages

print("Server is listening...")  # Display server listening status
receive()  # Start accepting client connections