import socket
import threading
import os

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 55555))
running = True
receiving_file = False

nickname = input("Choose your username: ")

# Create user directory for downloads
user_dir = nickname
if not os.path.exists(user_dir):
    os.makedirs(user_dir)
    print(f"Created download directory: {user_dir}")

def receive_file_tcp(filename, filesize):
    """Receive file via TCP."""
    global receiving_file
    try:
        filepath = os.path.join(user_dir, filename)
        received = 0

        with open(filepath, 'wb') as f:
            while received < filesize:
                chunk = client.recv(4096)
                if not chunk:
                    break
                # Check if we got FILE_END marker
                if b'FILE_END' in chunk:
                    data_part = chunk.split(b'FILE_END')[0]
                    if data_part:
                        f.write(data_part)
                        received += len(data_part)
                    break
                f.write(chunk)
                received += len(chunk)

        actual_size = os.path.getsize(filepath)
        print(f"\n[Downloaded] {filename} via TCP - {actual_size} bytes")
        print(f"[Saved to] {filepath}")
    except Exception as e:
        print(f"\nError downloading file: {e}")
    finally:
        receiving_file = False

def receive_file_udp(host, port, filename):
    """Receive file via UDP."""
    try:
        udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_sock.settimeout(5.0)

        # Request file
        udp_sock.sendto(f"REQUEST:{filename.strip()}".encode(), (host, port))

        # Receive start message with filesize
        data, _ = udp_sock.recvfrom(2048)
        msg = data.decode('utf-8', errors='ignore')

        if msg.startswith('ERROR:'):
            print(f"\n{msg}")
            return

        if msg.startswith('START:'):
            filesize = int(msg.split(':')[1])
            filepath = os.path.join(user_dir, filename)

            chunks = {}
            with open(filepath, 'wb') as f:
                while True:
                    try:
                        data, _ = udp_sock.recvfrom(2048)
                        msg = data.decode('utf-8', errors='ignore')

                        if data == b'END':
                            break

                        if data.startswith(b'DATA:'):
                            # Extract sequence number and data
                            parts = data.split(b':', 2)
                            if len(parts) == 3:
                                seq = int(parts[1])
                                chunk_data = parts[2]
                                chunks[seq] = chunk_data
                    except socket.timeout:
                        break

                # Write chunks in order
                for seq in sorted(chunks.keys()):
                    f.write(chunks[seq])

            actual_size = os.path.getsize(filepath)
            print(f"\n[Downloaded] {filename} via UDP - {actual_size} bytes")
            print(f"[Saved to] {filepath}")
    except Exception as e:
        print(f"\nError downloading via UDP: {e}")
    finally:
        udp_sock.close()

def receive():
    global running, receiving_file
    files_list = []
    collecting_files = False

    while running:
        try:
            message = client.recv(1024).decode('utf-8')
            if not message:
                break
            if message == 'NICK':
                client.send(nickname.encode('utf-8'))
            elif message == 'FILES_LIST_START':
                files_list = []
                collecting_files = True
            elif message == 'FILES_LIST_END':
                collecting_files = False
                if files_list:
                    print("\n=== Available Files ===")
                    for fname, fsize in files_list:
                        print(f"{fname:30} - {fsize:,} bytes")
                    print("=======================")
                    print("Use: /download <filename> <tcp|udp>")
            elif collecting_files and message.startswith('FILE:'):
                parts = message.split(':', 2)
                if len(parts) == 3:
                    files_list.append((parts[1], int(parts[2])))
            elif message.startswith('FILE_START:'):
                parts = message.split(':', 2)
                if len(parts) == 3:
                    filename = parts[1].strip()
                    filesize = int(parts[2])
                    receiving_file = True
                    receive_file_tcp(filename, filesize)
            elif message.startswith('FILE_ERROR:'):
                error = message.split(':', 1)[1]
                print(f"\n[Error] {error}")
            elif message.startswith('UDP_INFO:'):
                parts = message.split(':')
                if len(parts) == 4:
                    udp_host = parts[1]
                    udp_port = int(parts[2])
                    filename = parts[3].strip()
                    threading.Thread(target=receive_file_udp, args=(udp_host, udp_port, filename), daemon=True).start()
            else:
                if not receiving_file:
                    print(message)
        except:
            break
    client.close()

def write():
    global running
    while running:
        text = input()
        if text == '/quit':
            running = False
            client.close()
            print("You have left the chat.")
            break
        elif text == '/help':
            print("\n=== Commands ===")
            print("/msg <nickname> <message>    - Send private message")
            print("/join <group>                - Join a group")
            print("/leave <group>               - Leave a group")
            print("/group <group> <message>     - Send message to group")
            print("/files                       - List available files")
            print("/download <file> <tcp|udp>   - Download file")
            print("/help                        - Show this help")
            print("/quit                        - Exit chat")
            print("================")
        else:
            # Only send message, do NOT print locally
            client.send(f"{nickname}: {text}".encode('utf-8'))

thread_receive = threading.Thread(target=receive)
thread_receive.start()

thread_write = threading.Thread(target=write)
thread_write.start()