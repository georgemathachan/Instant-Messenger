import socket  # Import socket module for network communication
import threading  # Import threading module to handle multiple operations concurrently

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create TCP socket object
client.connect(('127.0.0.1', 55555))  # Connect to server on localhost at port 55555
running = True  # Global flag to control thread execution

nickname = input("Choose your username: ")  # Prompt user to enter their chat username

def receive():  # Function to continuously receive messages from server
    global running  # Access the global running flag
    while running:  # Keep receiving while client is active
        try:  # Try block to handle potential connection errors
            message = client.recv(1024).decode('utf-8')  # Receive up to 1024 bytes and decode to string
            if not message:  # Check if empty message (server disconnected)
                break  # Exit loop if no message received
            if message == 'NICK':  # Check if server is requesting nickname
                client.send(nickname.encode('utf-8'))  # Send nickname encoded as bytes
            else:  # If message is not nickname request
                print(message)  # Display the received message to user
        except:  # Catch any exceptions during receiving
            break  # Exit loop on error
    client.close()  # Close socket connection when done



def write():  # Function to handle sending user messages to server
    while True:  # Infinite loop for continuous message sending
        message = f'{nickname}: {input("")}'  # Format message with nickname prefix and user input
        client.send(message.encode('utf-8'))  # Encode and send message to server
        if message.endswith('/quit'):  # Check if user wants to quit
            running = False  # Set running flag to false to stop receive thread
            client.close()  # Close socket connection
            print("You have left the chat.")  # Inform user they've disconnected
            break  # Exit the write loop
thread_receive = threading.Thread(target=receive)  # Create thread for receiving messages
thread_receive.start()  # Start the receive thread
thread_write = threading.Thread(target=write)  # Create thread for writing messages
thread_write.start()  # Start the write thread
