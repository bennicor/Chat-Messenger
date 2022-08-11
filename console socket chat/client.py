import socket


HEADER = 2
DISCONNECT_MESSAGE = "DISCONNECT!"
PORT = 5050
SERVER = "192.168.1.64"
ADDR = (SERVER, PORT)
FORMAT = "utf-8"

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)

def send(msg):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    msg_length = str(msg_length).encode(FORMAT)
    msg_length += b" " * (HEADER - len(msg_length))
    print(msg_length)

    client.send(msg_length)
    client.send(message)

while True:
    msg = input()
    send(msg)