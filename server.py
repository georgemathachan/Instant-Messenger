import threading
import socket

host = '127.0.0.1'
port = 55555

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()
print(f"Server started on {host}:{port}")

clients = []
nicknames = []

def broadcast(message, sender=None):
    """
    Send message to all clients except the sender.
    If sender is None, send to everyone.
    """
    for client in clients:
        if client != sender:
            client.send(message)

def handle(client):
    while True:
        try:
            message = client.recv(1024)
            broadcast(message, sender=client)  # don't send back to sender
        except:
            if client in clients:
                index = clients.index(client)
                clients.remove(client)
                client.close()
                nickname = nicknames[index]
                nicknames.remove(nickname)
                # Broadcast leave message to everyone else
                broadcast(f"{nickname} left the chat!".encode('utf-8'))
            break

def receive():
    while True:
        client, address = server.accept()
        print(f"Connected with {str(address)}")

        client.send('NICK'.encode('utf-8'))
        nickname = client.recv(1024).decode('utf-8')
        nicknames.append(nickname)
        clients.append(client)

        print(f"Username of the client is {nickname}")
        # Broadcast join message to everyone except the new client
        broadcast(f"{nickname} joined the chat!".encode('utf-8'), sender=client)
        client.send('Connected to the server!'.encode('utf-8'))

        thread = threading.Thread(target=handle, args=(client,))
        thread.start()

print("Server is listening...")
receive()