from networking import SocketClient
from command import Move
import time

host = input("host: ")
port = int(input("port: "))

client = SocketClient(host, port)

client.send_command("hello")
time.sleep(10)
client.send_command("hello2")
client.sock.close()
