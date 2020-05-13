# content to include in message:
# message length, what type of message
# if type is 0 then command message:
# command id, command arguments


# client out job:
# send contents of game commands queue every frame, if nothing, do not send
# when requested, send copies of game objects to compare with the server
# when requested, respond to a ping from server to determine latency

# client in job:
# receive game commands in serialized format and decode, adding them to commands queue
# receive ping and get game state requests accordingly


# server out job:
# send all game updates to every client
# send game state requests at regular intervals to every client
# send ping requests to every client at regular intervals

# server in job:
# receive game commands from all clients and add to server queue
# receive game states from each client and compare them to server state
# receive ping replies from the client and store latency


# server threads:
# client thread to run for each connection

import threading
import socket


class SocketServer:
    HEADER_LENGTH = 10
    COMMAND_LENGTH = 3

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))

        self.clients = {}  # client: username

    def listen(self):
        self.sock.listen(5)
        while True:
            client, address = self.sock.accept()
            self.clients[client] = "username"
            client.settimeout(60)
            threading.Thread(target=self.client_thread(), args=(client, address)).start()

    def client_thread(self):
        pass

    def receive_message(self, client):
        length = int(client.recv(self.HEADER_LENGTH))
        message_id = int(client.recv(self.COMMAND_LENGTH))
        message_content = client.recv
        print(length, message_id)

