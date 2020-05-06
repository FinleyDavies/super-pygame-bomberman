import socket
import select
import threading

HEADERSIZE = 10
IP = socket.gethostname()
PORT = 5556

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((IP, PORT))
s.listen()

clients = {}


def move(player, content):
	print(f"{player} has made a move to {content}")


def say(player, content):
	print(f"{player} has said {content}")


commands = {"/move": move, "/say": say}


def receive_command(client_socket):
	length = client_socket.rcv(HEADERSIZE)
	if length is None:
		print("a client has disconnected")
		return 0

	length = int(length.decode())
	command = client_socket.rcv(length).decode()
	command = command.split()

	response = commands[command[0]](command[1]).encode()
	header = f"{len(response):<{HEADERSIZE}}".encode()
	client_socket.send(header + response)
