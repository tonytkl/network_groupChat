import socket
import sys
import selectors
import msvcrt

HOST = 'localhost'
PORT = 8080

def main(address, port):
    sel = selectors.DefaultSelector()

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((address, port))
    print("Connected to the server")

    sel.register(client, selectors.EVENT_READ)
    
    while True:
        events = sel.select(timeout=1)
        for key, _ in events:
            if key.fileobj == client:
                message = client.recv(2048)
                if message:
                    print(message.decode())
                else:
                    print("Disconnected from server")
                    sel.unregister(client)
                    client.close()
                    return

if __name__ == "__main__":
    main(HOST, PORT)