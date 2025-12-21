import socket
import select
import sys

HOST = '127.0.0.1'
PORT = 55555
BUFFER_SIZE = 1024

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))
client.setblocking(False)

nickname = input("Choose your username: ")

while True:
    sockets = [client, sys.stdin]

    read_sockets, _, _ = select.select(sockets, [], [])

    for sock in read_sockets:

        # Incoming server message
        if sock == client:
            message = client.recv(BUFFER_SIZE)
            if not message:
                print("Disconnected from server")
                sys.exit()

            decoded = message.decode()

            if decoded == "NICK":
                client.send(nickname.encode())
            else:
                print(decoded)

        # User typed something
        else:
            msg = sys.stdin.readline()
            if msg:
                client.send(f"{nickname}: {msg}".encode())

