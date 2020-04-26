import socket

HEADER_LENGTH = 10
HOST = socket.gethostname()
PORT = 1234

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(5)

while True:
	client_socket, address = s.accept()
	print(address)
	msg = bytes("Connection established", "utf-8")
	msg = bytes(f"{len(msg):<{HEADER_LENGTH}}", "utf-8") + msg
	client_socket.send(msg)
	msg = bytes("Connection established", "utf-8")
	msg = bytes(f"{len(msg):<{HEADER_LENGTH}}", "utf-8") + msg
	client_socket.send(msg)
