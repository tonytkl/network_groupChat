import tkinter as tk
from tkinter import simpledialog
import threading
import socket

HOST = 'localhost'
PORT = 8080

class ChatClient:
    def __init__(self, root):
        self.root = root
        self.root.title("Chat Client")

        self.chat_box = tk.Text(root, state='disabled', width=50, height=20)
        self.chat_box.pack(padx=10, pady=10)

        self.input_box = tk.Entry(root, width=50)
        self.input_box.pack(padx=10, pady=10)
        self.input_box.bind("<Return>", self.send_message)

        self.name = simpledialog.askstring("Name", "Enter your name:")
        if self.name:
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.connect((HOST, PORT))
            self.client.send(f"name-{self.name}".encode())

            threading.Thread(target=self.receive_messages, daemon=True).start()

    def send_message(self, event=None):
        message = self.input_box.get()
        self.client.send(message.encode())
        self.input_box.delete(0, tk.END)

    def receive_messages(self):
        while True:
            try:
                message = self.client.recv(1024).decode()
                self.chat_box.config(state='normal')
                self.chat_box.insert(tk.END, f"{message}\n")
                self.chat_box.config(state='disabled')
                self.chat_box.see(tk.END)
            except:
                break

if __name__ == "__main__":
    root = tk.Tk()
    client = ChatClient(root)
    root.mainloop()
