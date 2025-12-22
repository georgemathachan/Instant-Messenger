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
                print(message)
        except:
            break
    client.close()



def write():
    while True:
        message = f'{nickname}: {input("")}'
        client.send(message.encode('utf-8'))
        if message.endswith('/quit'):
            running = False
            client.close()
            print("You have left the chat.")
            break
thread_receive = threading.Thread(target=receive)
thread_receive.start()
thread_write = threading.Thread(target=write)
thread_write.start()
