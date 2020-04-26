import socket

HEADER_LENGTH = 10
HOST = socket.gethostname()
PORT = 1234

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

while True:
	full_msg = ""
	new_msg = True
	while True:
		msg = s.recv(16).decode("utf-8")
		if new_msg:
			print(f"new message length: {msg[:HEADER_LENGTH]}")
			length = int(msg[:HEADER_LENGTH])
			new_msg = False
		full_msg += msg
		if len(full_msg) - HEADER_LENGTH == length:
			print("full message received")
			print(full_msg[HEADER_LENGTH:])
			new_msg = True
