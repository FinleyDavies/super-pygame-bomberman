from communication import *
import socket
import time

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((socket.gethostname(), 1123))  # Bind to localhost for testing
s.listen(5)

p = Packet("message", "Welcome to the server!")

while True:
	client_socket, address = s.accept()
	print(f"Accepted connection from {address[0]} on port {address[1]}")
	send_message(client_socket, "Connected to the server!")
	p.send(client_socket)
	client_socket.close()