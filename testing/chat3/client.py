import socket
import errno
import sys
import threading
import time

HEADER_LENGTH = 10
IP = "192.168.1.2"
PORT = 1234

my_username = input("Username: ")

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((IP, PORT))
client_socket.setblocking(False)

username = bytes(my_username, "utf-8")
username = bytes(f"{len(username):<{HEADER_LENGTH}}", "utf-8") + username
client_socket.send(username)

def receive_message(name):
	while True:
		try:
			while True:
				username_header = client_socket.recv(HEADER_LENGTH)
				if not username_header:
					print("connection closed by the server")
					input()
					sys.exit()

				username_length = int(username_header.decode("utf-8"))
				username = client_socket.recv(username_length).decode("utf-8")

				message_header = client_socket.recv(HEADER_LENGTH)
				message_length = int(message_header.decode("utf-8"))
				message = client_socket.recv(message_length).decode("utf-8")

				print(f"{username}: {message}")

		except IOError as e:
			if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
				print(str(e))
				input()
				sys.exit()
			#print(e)
			time.sleep(1)
			continue


x = threading.Thread(target=receive_message, args=(1,))
x.start()
while True:
	message = input()

	if message:
		message = message.encode("utf-8")
		message_header = f"{len(message):<{HEADER_LENGTH}}".encode("utf-8")
		client_socket.send(message_header + message)