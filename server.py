import socket
import select

HOST = '127.0.0.1'
PORT = 55555
BUFFER_SIZE = 1024

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((HOST, PORT))
server.listen()
server.setblocking(False)

sockets_list = [server]
clients = {}  # socket -> nickname

print(f"Server started on {HOST}:{PORT}")

def broadcast(message, sender_socket=None):
    for sock in clients:
        if sock != sender_socket:
            sock.send(message)

while True:
    read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)

    for notified_socket in read_sockets:

        # New connection
        if notified_socket == server:
            client_socket, client_address = server.accept()
            client_socket.setblocking(False)

            sockets_list.append(client_socket)
            client_socket.send(b"NICK")

            print(f"Connection from {client_address}")

        # Existing client sent a message
        else:
            try:
                message = notified_socket.recv(BUFFER_SIZE)

                # Client disconnected
                if not message:
                    nickname = clients[notified_socket]
                    print(f"{nickname} disconnected")

                    sockets_list.remove(notified_socket)
                    del clients[notified_socket]
                    notified_socket.close()

                    broadcast(f"{nickname} left the chat!".encode())
                    continue

                # First message = nickname
                if notified_socket not in clients:
                    nickname = message.decode().strip()
                    clients[notified_socket] = nickname
                    print(f"Username set to {nickname}")
                    broadcast(f"{nickname} joined the chat!".encode())
                    notified_socket.send(b"Connected to the server!")
                else:
                    broadcast(message, notified_socket)

            except:
                nickname = clients.get(notified_socket, "Unknown")
                sockets_list.remove(notified_socket)
                clients.pop(notified_socket, None)
                notified_socket.close()
                broadcast(f"{nickname} left the chat!".encode())

    for notified_socket in exception_sockets:
        sockets_list.remove(notified_socket)
        clients.pop(notified_socket, None)
        notified_socket.close()