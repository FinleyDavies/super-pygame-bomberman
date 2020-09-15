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
import queue
import game_commands
import time
import json
from collections import OrderedDict


# todo completely redo with either select or asyncio

# todo fix problem where timed out clients are not removed from client list in SocketServer

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


class ThreadedIO:
    HEADER_LENGTH = 10
    COMMAND_LENGTH = 3

    def __init__(self, sock, adress, server=None):
        self.sock = sock
        self.server = server
        self.connected = True
        self.input_queue = queue.Queue()
        self.output_queue = queue.Queue()

        self.t1 = threading.Thread(target=self.input, args=(self.sock,), name="ThreadedIO input")
        self.t2 = threading.Thread(target=self.output, args=(self.sock,), name="ThreadedIO output")
        self.t1.setDaemon(True)
        self.t2.setDaemon(True)
        self.t1.start()
        self.t2.start()


    def input(self, sock):
        while self.connected:
            try:
                header = sock.recv(self.HEADER_LENGTH)
                if header:
                    length = int(header)
                    message_id = int(sock.recv(self.COMMAND_LENGTH))

                    message_content = sock.recv(length)
                    message_content = message_content.decode("utf-8")
                    self.input_queue.put((message_id, message_content))
                    # print(
                    #     f"(ThreadedIO {time.strftime('%H:%M:%S', time.localtime())}) Message '{message_content}' received from {sock.getsockname()}")
                    # print(f"\tMessage id: {message_id} \n\tlength: {length}")

                else:
                    # print(f"(ThreadedIO) Empty header from {sock.getsockname()}")
                    self.connected = False
                    self.output_queue.put([999, ""])
                    break

            except ConnectionResetError:
                print(f"(ThreadedIO) {sock.getsockname()} disconnected unexpectedly")
                self.close()
                break

            except (OSError, ConnectionAbortedError):
                print(f"(ThreadedIO) Server closed socket")
                self.close()
                # self.connected = False
                break

    def output(self, sock):
        while self.connected:
            message_id, message_content = self.output_queue.get()

            if message_id == 999:
                break

            message_content = message_content
            message_content = message_content.encode("utf-8")

            id_header = f"{message_id:<{self.COMMAND_LENGTH}}".encode("utf-8")
            length_header = f"{len(message_content):<{self.HEADER_LENGTH}}".encode("utf-8")

            sock.send(length_header + id_header + message_content)
            # print(f"(ThreadedIO) Message '{message_content.decode('utf-8')}' sent to {sock.getsockname()}")

    def close(self):
        # self.output_queue.put((999, ""))
        self.connected = False
        self.sock.close()
        print("closing")
        if self.server is not None:
            self.server.remove_sock_io(self)

    def put_output(self, message_id: int, message_content: str):
        self.output_queue.put((message_id, message_content))

    def get_input(self):
        return self.input_queue.get()

    def input_empty(self):
        return self.input_queue.empty()


class SocketServer:
    HEADER_LENGTH = 10
    COMMAND_LENGTH = 3
    TIMEOUT = 120

    def __init__(self, dc_callback, host=0, port=0):
        if host == 0:
            host = get_ip()
        if port == 0:
            port = 4832

        self.host = host
        self.port = port
        self.dc_callback = dc_callback
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        self.start_time = time.time()

        self.clients = OrderedDict()  # client: {username: , ThreadedIO: }
        # using ordereddict to preserve order in which players join, and decide their colour and player no accordingly

    def start_listening(self):
        threading.Thread(target=self.listen).start()

    def listen(self):
        self.sock.listen(5)
        # print(f"(SocketServer) Server started listening for connections on {self.sock.getsockname()}")
        while True:
            # print("(SocketServer) Waiting for connection")
            client, address = self.sock.accept()
            client.settimeout(self.TIMEOUT)
            # print(f"(SocketServer) connection from {client.getsockname()}, address: {address}")

            sock_io = ThreadedIO(client, address, self)
            _, username = sock_io.get_input()
            while username in self.clients:
                try:
                    username = username[:-1] + str(int(username[-1]) + 1)
                except ValueError:
                    username = username + "1"

            sock_io.put_output(0, username)
            self.clients[username] = sock_io

    def send_to_all(self, message, exclude=None):
        # print(message)
        exclude = [] if exclude is None else exclude
        # sends the message to all clients
        for username, sock_io in self.clients.items():
            if username not in exclude:
                sock_io.put_output(message[0], message[1])

    def send_message(self, message, usernames):
        # print(message)
        for username in usernames:
            self.clients[username].put_output(message[0], message[1])

    def collect_messages(self):
        messages = []
        for username, client in self.clients.items():
            while not client.input_empty():
                messages.append((client.get_input(), username))
        return messages

    def remove_sock_io(self, to_remove):
        print(f"removing {to_remove} from server")
        print(self.clients)
        for username, sock_io in self.clients.items():
            if sock_io == to_remove:
                print(f"sockio username is {username}")
                client = self.clients.pop(username)
                if sock_io.connected:
                    client.close()
                print(self.clients)
                self.dc_callback(self, username)
                break



    def get_uptime(self):
        return time.time() - self.start_time

    def kill(self):
        # end every ThreadedIO thread and call .join(), as well as closing all connections gracefully
        pass

    def get_clients(self):
        return self.clients


class SocketClient:
    HEADER_LENGTH = 10
    COMMAND_LENGTH = 3

    def __init__(self, host, port, username):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))
        self.sock_io = ThreadedIO(self.sock, (self.host, self.port))
        self.username = self._connect(username)

    def send_message(self, message):
        self.sock_io.put_output(message[0], message[1])
        # print(f"(SocketClient) sent {message[1]}")

    def receive_message(self):
        return self.sock_io.get_input()

    def collect_messages(self):
        messages = []
        while not self.empty():
            messages.append(self.receive_message())
        return messages

    def _connect(self, username):
        self.send_message([0, username])
        return self.receive_message()[1]

    def empty(self):
        return self.sock_io.input_empty()

    def get_username(self):
        return self.username

    def close(self):
        print("closing connection")
        self.sock_io.close()
