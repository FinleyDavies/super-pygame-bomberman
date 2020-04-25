import socket
import select

HEADER_LENGTH = 10
IP = socket.gethostbyname(socket.gethostname())
PORT = 1234

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server_socket.bind((IP, PORT))
server_socket.listen()

socket_list = [server_socket]

clients = {}


def receive_message(client_socket):
	try:
		message_header = client_socket.recv(HEADER_LENGTH)
		if not message_header:
			return False

		message_length = int(message_header.decode("utf-8"))

		return {"header": message_header, "data": client_socket.recv(message_length)}

	except:
		return False


while True:
	read_sockets, _, exception_sockets = select.select(socket_list, [], socket_list)
	for notified_socket in read_sockets:
		if notified_socket == server_socket:
			client_socket, client_address = server_socket.accept()
			user = receive_message(client_socket)

			if user is False:
				continue

			socket_list.append(client_socket)
			clients[client_socket] = user
			print(client_address, user["data"].decode("utf-8"))

		else:
			msg = receive_message(notified_socket)
			if msg is False:
				print(clients[notified_socket]["data"].decode("utf-8"), "Disconnected")
				socket_list.remove(notified_socket)
				del clients[notified_socket]
				continue
			else:
				print(f"{clients[notified_socket]['data'].decode('utf-8')}: {msg['data'].decode('utf-8')}")
