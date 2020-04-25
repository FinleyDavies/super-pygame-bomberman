import socket
import pickle
import time

HEADER_LENGTH = 10


def send_message(target, message):
	length = len(message)
	encoded = bytes(f"{length:<{HEADER_LENGTH}}{message}", "utf-8")
	target.send(encoded)


def receive_message(sender):
	message_length = sender.recv(HEADER_LENGTH).decode("utf-8").strip()
	if message_length:
		length = int(message_length)

		if length < 2**(HEADER_LENGTH-1):
			message = sender.recv(length)
			return message.decode("utf-8")

		else:
			length -= 2**(HEADER_LENGTH-1)
			packet = sender.recv(length)
			packet = pickle.loads(packet)
			if packet.type == "message":
				return packet.contents


	return 0



class Packet:
	def __init__(self, type, contents):
		self.type = type
		self.contents = contents
		self.time_sent = 0

	def send(self, target):
		self.time_sent = time.time()
		message_bytes = pickle.dumps(self)
		length = len(message_bytes)
		length += 2 ** (HEADER_LENGTH - 1)
		encoded = bytes(f"{length:<{HEADER_LENGTH}}", "utf-8") + message_bytes
		target.send(encoded)