import socket
import pickle

HEADER_LENGTH = 10


class Server:
	def __init__(self, port, address=None):
		self.port = port

		if address is None:
			address = socket.gethostbyname(socket.gethostname())


def receive_packet(client_socket):
	pass
