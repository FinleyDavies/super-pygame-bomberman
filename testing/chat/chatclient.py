from communication import *
import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((socket.gethostname(), 1123))

while True:
	m = receive_message(s)
	if m:
		print(m, "\n")
		ping(s)
		print(s.getsockname())
		print(socket.gethostbyname(socket.gethostname()))
		print(socket.get)