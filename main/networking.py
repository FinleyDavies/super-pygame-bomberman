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
import command
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


class ThreadedIO:
    HEADER_LENGTH = 10
    COMMAND_LENGTH = 3

    def __init__(self, sock):
        self.sock = sock
        self.connected = True
        self.input_queue = queue.Queue()
        self.output_queue = queue.Queue()

        threading.Thread(target=self.input, args=(self.sock,)).start()
        threading.Thread(target=self.output, args=(self.sock,)).start()

    def input(self, sock):
        while self.connected:
            try:
                header = sock.recv(self.HEADER_LENGTH)
                if header:
                    length = int(header)
                    message_id = int(sock.recv(self.COMMAND_LENGTH))

                    if message_id == 998:
                        print(f"(ThreadedIO) {sock.getsockname()} disconnected gracefully")
                        self.connected = False
                        self.output_queue.put([999, ""])
                        break

                    message_content = sock.recv(length).decode("utf-8")
                    self.input_queue.put((message_id, message_content))
                    print(f"(ThreadedIO {time.strftime('%H:%M:%S', time.localtime())}) Message '{message_content}' received from {sock.getsockname()}")
                    print(f"\tMessage id: {message_id} \n\tlength: {length}")

                else:
                    print(f"(ThreadedIO) Empty header from {sock.getsockname()}")

            except ConnectionResetError:
                print(f"(ThreadedIO) {sock.getsockname()} disconnected unexpectedly")
                self.connected = False
                self.output_queue.put([999, ""])  # Stop the queue.get() in output thread blocking and close connection
                break

            except (OSError, ConnectionAbortedError):
                print(f"(ThreadedIO) disconnected gracefully")
                #self.connected = False
                #break

    def output(self, sock):
        while self.connected:
            message_id, message_content = self.output_queue.get()

            if message_id == 999:
                self.connected = False
                sock.close()
                self.input_queue.put(None)
                break

            message_content = message_content.encode("utf-8")

            id_header = f"{message_id:<{self.COMMAND_LENGTH}}".encode()
            length_header = f"{len(message_content):<{self.HEADER_LENGTH}}".encode()

            sock.send(length_header + id_header + message_content)
            print(f"(ThreadedIO) Message '{message_content.decode('utf-8')}' sent to {sock.getsockname()}")

    def close(self):
        self.output_queue.put((998, ""))
        self.output_queue.put((999, ""))

    def put_output(self, message_id: int, message_content: str):
        self.output_queue.put((message_id, message_content))

    def get_input(self, blocking=False):
        # gets the next input from the input queue, returns None if queue is empty
        if not blocking and self.input_queue.empty():
            return None

        return self.input_queue.get()


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

        self.clients = {}  # client: {username: , ThreadedIO: }

    def start_listening(self):
        threading.Thread(target=self.listen).start()

    def listen(self):
        self.sock.listen(5)
        print(f"(SocketServer) Server started listening for connections on {self.sock.getsockname()}")
        while True:
            print("(SocketServer) Waiting for connection")
            client, address = self.sock.accept()
            client.settimeout(60)
            print(f"(SocketServer) connection from {client.getsockname()}, address: {address}")

            sock_io = ThreadedIO(client)
            time.sleep(3)
            _, username = sock_io.get_input(True)
            print(username)
            self.clients[address] = {"username": username, "sockIO": sock_io}

    def send_to_all(self, message):
        # sends the message to all clients
        for client in self.clients.values():
            client["sockIO"].put_output(message[0], message[1])

    def kill(self):
        # end every ThreadedIO thread and call .join(), as well as closing all connections gracefully
        pass


class SocketClient:
    HEADER_LENGTH = 10
    COMMAND_LENGTH = 3

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))
        self.sock_io = ThreadedIO(self.sock)

    def send_message(self, message):
        self.sock_io.put_output(message[0], message[1])
        print(f"(SocketClient) sent {message[1]}")

    def receive_message(self):
        print(self.sock_io.get_input())
