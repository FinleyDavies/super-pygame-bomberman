import socket
import select
import errno

HEADER_LENGTH = 10
IP = "127.0.0.1"
PORT = 1234

my_username = input("Username: ")

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((IP, PORT))
client_socket.setblocking(False)

username = bytes(my_username, "utf-8")
username = bytes(f"{len(username):<{HEADER_LENGTH}}", "utf-8") + username
client_socket.send(username)

