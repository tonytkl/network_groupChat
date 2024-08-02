import socket
import selectors

HOST = 'localhost'
PORT = 8080

sel = selectors.DefaultSelector()
clients = []
named_clients = []

def accept(sock):
    conn, addr = sock.accept()
    print(f"Connected by {addr}")
    conn.setblocking(False)
    sel.register(conn, selectors.EVENT_READ, read)
    print(f"Registered {conn}")
    clients.append(conn)
    named_clients.append({"conn": conn, "name": ""})

def read(conn):
    try:
        data = conn.recv(1024)
        if data:
            if data.decode().startswith("name-"):
                for client in named_clients:
                    if client["conn"] == conn:
                        client["name"] = data.decode().split("-")[1]
            else:
                broadcast(data, conn)
        else:
            disconnect(conn)
    except ConnectionResetError:
        disconnect(conn)

def broadcast(message, sender):
    # Find the client's name based on the connection object
    client_name = None
    for client in named_clients:
        if client['conn'] == sender:
            client_name = client['name']
            break
    
    # If client_name is found, use it; otherwise, use the sender object
    if client_name:
        formatted_message = f"<{client_name}>: {message.decode()}"
    else:
        formatted_message = f"<{sender}>: {message.decode()}"
    
    # Encode the message
    encoded_message = formatted_message.encode()
    
    # Broadcast the message to all clients
    for client in named_clients:
        client['conn'].send(encoded_message)

def disconnect(conn):
    print(f"Disconnected {conn}")
    sel.unregister(conn)
    clients.remove(conn)
    named_clients.remove([client for client in named_clients if client["conn"] == conn][0])
    conn.close()

def main(address, port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((address, port))
    server.listen()
    print(f"Server started on {address}:{port}")
    server.setblocking(False)
    sel.register(server, selectors.EVENT_READ, accept)

    while True:
        events = sel.select()
        for key, mask in events:
            callback = key.data
            callback(key.fileobj)

if __name__ == "__main__":
    main(HOST, PORT)