import threading
import socket

host = '127.0.0.1'
port = 55555

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((host, port))
server.listen()
print(f"Server started on {host}:{port}")

clients = []
nicknames = []
groups = {}

def broadcast(message, sender=None):
    """
    Send message (bytes) to all clients except the sender.
    If sender is None, send to everyone.
    """
    for client in clients:
        if client != sender:
            client.send(message)

def send_text(sock, text):
    """Helper to send UTF-8 text as bytes."""
    try:
        sock.send(text.encode('utf-8'))
    except:
        pass

def format_chat(nick, text):
    """Create standard chat line '<nick>: <text>'"""
    return f"{nick}: {text}"

def handle(client):
    while True:
        try:
            data = client.recv(1024)
            if not data:
                raise ConnectionError()

            # Resolve sender nickname
            if client in clients:
                sender_idx = clients.index(client)
                sender_nick = nicknames[sender_idx]
            else:
                sender_nick = "Unknown"

            decoded = data.decode('utf-8', errors='ignore').strip()

            # If the client sent with a '<nick>: ' prefix, strip it to avoid double-nick
            if decoded.startswith(f"{sender_nick}: "):
                decoded = decoded[len(sender_nick) + 2:]

            # Commands
            if decoded.startswith('/msg '):
                try:
                    _, target, text = decoded.split(' ', 2)
                    if target in nicknames:
                        target_client = clients[nicknames.index(target)]
                        send_text(target_client, f"[Private] {sender_nick}: {text}")
                        # Optional feedback to sender
                        send_text(client, f"[To {target}] {text}")
                    else:
                        send_text(client, f"User '{target}' not found")
                except ValueError:
                    send_text(client, "Usage: /msg <nickname> <message>")

            elif decoded.startswith('/join '):
                parts = decoded.split(' ', 1)
                group = parts[1].strip() if len(parts) > 1 else ''
                if not group:
                    send_text(client, "Usage: /join <group>")
                else:
                    members = groups.setdefault(group, set())
                    members.add(client)
                    send_text(client, f"Joined group '{group}'")
                    # Notify group members except sender
                    for m in list(members):
                        if m != client:
                            send_text(m, f"{sender_nick} joined group '{group}'")

            elif decoded.startswith('/leave '):
                parts = decoded.split(' ', 1)
                group = parts[1].strip() if len(parts) > 1 else ''
                if not group:
                    send_text(client, "Usage: /leave <group>")
                else:
                    members = groups.get(group)
                    if members and client in members:
                        members.remove(client)
                        send_text(client, f"Left group '{group}'")
                        for m in list(members):
                            send_text(m, f"{sender_nick} left group '{group}'")
                        if not members:
                            # Clean up empty group
                            groups.pop(group, None)
                    else:
                        send_text(client, f"Not a member of group '{group}'")

            elif decoded.startswith('/group '):
                try:
                    _, group, text = decoded.split(' ', 2)
                except ValueError:
                    send_text(client, "Usage: /group <group> <message>")
                    continue
                members = groups.get(group)
                if not members or client not in members:
                    send_text(client, f"You are not in group '{group}'")
                else:
                    for m in list(members):
                        if m != client:
                            send_text(m, f"[{group}] {sender_nick}: {text}")

            else:
                # Normal broadcast chat
                line = format_chat(sender_nick, decoded)
                broadcast(line.encode('utf-8'), sender=client)

        except:
            # Disconnect cleanup
            if client in clients:
                index = clients.index(client)
                clients.remove(client)
                client.close()
                nickname = nicknames[index]
                nicknames.remove(nickname)
                # Remove from all groups
                for g, members in list(groups.items()):
                    if client in members:
                        members.remove(client)
                        for m in list(members):
                            send_text(m, f"{nickname} left group '{g}'")
                        if not members:
                            groups.pop(g, None)
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