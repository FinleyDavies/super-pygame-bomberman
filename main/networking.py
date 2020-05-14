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
import time
import json


# todo completely redo with either select or asyncio

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP


class SocketServer:
    HEADER_LENGTH = 10
    COMMAND_LENGTH = 3

    def __init__(self, host=0, port=0):
        if host == 0:
            host = get_ip()
        if port == 0:
            port = 4832
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))

        self.clients = {}  # client: username

        self.game_commands = []
        self.command_lock = threading.Lock()

    def start_listening(self):
        threading.Thread(target=self.listen).start()

    def listen(self):
        self.sock.listen(5)
        print(self.host, self.port)
        print(self.sock.getsockname())
        while True:
            print("waiting for connections")
            client, address = self.sock.accept()
            print(f"connection from {client}, {address}")
            self.clients[client.getsockname()] = "username"
            client.settimeout(60)
            threading.Thread(target=self.client_thread, args=(client, address)).start()

    def client_thread(self, client, address):
        while True:
            try:
                ret = self.receive_message(client)
                if ret == 1:
                    client.send("command received by server".encode())
                    print(self.get_commands())
                elif ret == 0:
                    raise Exception

            except:
                print(client.getsockname(), "disconnected")
                self.clients.pop(client.getsockname())
                client.close()
                return False

    def receive_message(self, client):
        header = client.recv(self.HEADER_LENGTH)
        if not header:
            return 0

        length = int(header)
        message_id = int(client.recv(self.COMMAND_LENGTH))
        message_content = client.recv(length)

        if message_id == 1:
            with self.command_lock:
                self.game_commands.append(message_content)
            return 1

    def get_commands(self):
        with self.command_lock:
            return self.game_commands

    def clear_commands(self):
        with self.command_lock:
            self.game_commands = list()


class SocketClient:
    HEADER_LENGTH = 10
    COMMAND_LENGTH = 3

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))

    def send_command(self, command):
        content = command.encode()
        header = f"{len(content):<{self.HEADER_LENGTH}}".encode()
        id = f"{1:<{self.COMMAND_LENGTH}}".encode()

        self.sock.send(header + id + content)
        print(self.sock.recv(100).decode())
