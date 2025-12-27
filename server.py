import threading
import socket
import os


host = '127.0.0.1'
port = 55555
file_port = 55556  # UDP port for file transfers
shared_dir = os.environ.get("SERVER_SHARED_FILES", "./SharedFiles")

# Create shared directory if it doesn't exist
if not os.path.exists(shared_dir):
    os.makedirs(shared_dir)
    print(f"Created shared files directory: {shared_dir}")

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((host, port))
server.listen()
print(f"Server started on {host}:{port}")
print(f"File transfer port (UDP): {file_port}")
print(f"Shared files directory: {shared_dir}")

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
    """Helper to send UTF-8 text as bytes with newline delimiter."""
    try:
        sock.sendall((text + "\n").encode('utf-8'))
    except:
        pass

def format_chat(nick, text):
    """Create standard chat line '<nick>: <text>'"""
    return f"{nick}: {text}"

def get_file_list():
    """Get list of files in shared directory with sizes."""
    try:
        files = []
        for filename in os.listdir(shared_dir):
            filepath = os.path.join(shared_dir, filename)
            if os.path.isfile(filepath):
                size = os.path.getsize(filepath)
                files.append((filename, size))
        return files
    except Exception as e:
        print(f"Error listing files: {e}")
        return []

def send_file_tcp(client_sock, filename):
    """Send file to client via TCP."""
    try:
        filepath = os.path.join(shared_dir, filename)
        if not os.path.exists(filepath):
            send_text(client_sock, "FILE_ERROR:File not found")
            return

        filesize = os.path.getsize(filepath)
        send_text(client_sock, f"FILE_START:{filename}:{filesize}")

        with open(filepath, 'rb') as f:
            while True:
                chunk = f.read(4096)
                if not chunk:
                    break
                client_sock.send(chunk)

        send_text(client_sock, "FILE_END")
        print(f"Sent file {filename} via TCP ({filesize} bytes)")
    except Exception as e:
        print(f"Error sending file {filename}: {e}")
        send_text(client_sock, f"FILE_ERROR:{str(e)}")

def handle_udp_file_transfer():
    """Handle UDP file transfer requests."""
    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_sock.bind((host, file_port))
    print(f"UDP file transfer server listening on {host}:{file_port}")

    while True:
        try:
            data, addr = udp_sock.recvfrom(1024)
            request = data.decode('utf-8', errors='ignore')

            if request.startswith('REQUEST:'):
                filename = request.split(':', 1)[1]
                filepath = os.path.join(shared_dir, filename)

                if not os.path.exists(filepath):
                    udp_sock.sendto(b"ERROR:File not found", addr)
                    continue

                filesize = os.path.getsize(filepath)
                # Send file info
                udp_sock.sendto(f"START:{filesize}".encode(), addr)

                # Send file data in chunks
                with open(filepath, 'rb') as f:
                    seq = 0
                    while True:
                        chunk = f.read(1024)
                        if not chunk:
                            break
                        udp_sock.sendto(f"DATA:{seq}:".encode() + chunk, addr)
                        seq += 1

                udp_sock.sendto(b"END", addr)
                print(f"Sent file {filename} via UDP to {addr} ({filesize} bytes)")
        except Exception as e:
            print(f"UDP error: {e}")

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
            elif decoded == '/files':
                files = get_file_list()
                if not files:
                    send_text(client, "No files available in shared directory")
                else:
                    send_text(client, "FILES_LIST_START")
                    for filename, size in files:
                        send_text(client, f"FILE:{filename}:{size}")
                    send_text(client, "FILES_LIST_END")

            elif decoded.startswith('/download '):
                parts = decoded.split()
                if len(parts) < 3:
                    send_text(client, "Usage: /download <filename> <tcp|udp>")
                else:
                    filename = parts[1]
                    protocol = parts[2].lower()

                    if protocol == 'tcp':
                        send_file_tcp(client, filename)
                    elif protocol == 'udp':
                        # Send UDP server info to client
                        send_text(client, f"UDP_INFO:{host}:{file_port}:{filename}")
                    else:
                        send_text(client, "Protocol must be 'tcp' or 'udp'")

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

# Start UDP file transfer handler in background
udp_thread = threading.Thread(target=handle_udp_file_transfer, daemon=True)
udp_thread.start()

print("Server is listening...")
receive()