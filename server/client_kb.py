import socket

HOST = 'localhost'
PORT = 8080

def main(address, port):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((address, port))

    name = input("Enter your name: ")
    client.send(f"name-{name}".encode())
    
    while True:
        
            message = input("\nEnter message: ")
            client.send(message.encode())


if __name__ == "__main__":
    main(HOST, PORT)