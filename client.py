import socket
import threading

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 55555))
running = True

nickname = input("Choose your username: ")

def receive():
    global running
    while running:
        try:
            message = client.recv(1024).decode('utf-8')
            if not message:
                break
            if message == 'NICK':
                client.send(nickname.encode('utf-8'))
            else:
                print(message)  # Print all messages from server (including your own)
        except:
            break
    client.close()

def write():
    global running
    while running:
        text = input()
        if text == '/quit':
            running = False
            client.send(f"{nickname} has left the chat.".encode('utf-8'))
            client.close()
            print("You have left the chat.")
            break
        # Only send message, do NOT print locally
        client.send(f"{nickname}: {text}".encode('utf-8'))

thread_receive = threading.Thread(target=receive)
thread_receive.start()

thread_write = threading.Thread(target=write)
thread_write.start()
