import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import socket
import selectors
from db.db_connection import create_connection, initial_setup, terminate_connection, add_user, add_message

HOST = 'localhost'
PORT = 8080

sel = selectors.DefaultSelector()
clients = []
named_clients = []


def accept(sock, db_connection):
    conn, addr = sock.accept()
    print(f"Connected by {addr}")
    conn.setblocking(False)
    sel.register(conn, selectors.EVENT_READ, lambda x: read(conn, db_connection))
    print(f"Registered {conn}")
    clients.append(conn)
    named_clients.append({"conn": conn, "name": ""})

def read(conn, db_connection):
    try:
        data = conn.recv(1024)
        if data:
            if data.decode().startswith("name-"):
                for client in named_clients:
                    if client["conn"] == conn:
                        client["name"] = data.decode().split("-")[1]
                        add_user(db_connection, f"{conn.getpeername()[0]}:{conn.getpeername()[1]}", client["name"])
            else:
                broadcast(data, conn, db_connection)
        else:
            disconnect(conn)
    except ConnectionResetError:
        disconnect(conn)

def broadcast(message, sender, db_connection):
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
    
    # Save the message to the database
    add_message(db_connection, f"{sender.getpeername()[0]}:{sender.getpeername()[1]}", message.decode())
    
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
    db_con = None
    try:
        # DB connection
        db_con = create_connection()
        initial_setup(db_con)

        # Server setup
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((address, port))
        server.listen()
        print(f"Server started on {address}:{port}")
        server.setblocking(False)
        sel.register(server, selectors.EVENT_READ, lambda x: accept(server, db_con))

        while True:
            events = sel.select()
            for key, mask in events:
                callback = key.data
                callback(key.fileobj)
    finally:
        terminate_connection(db_con)

if __name__ == "__main__":
    main(HOST, PORT)