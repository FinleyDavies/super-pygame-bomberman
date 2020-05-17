from networking import SocketClient
from command import Move
import time

host = "192.168.0.55"  # input("host: ")
port = 4832  # int(input("port: "))

client = SocketClient(host, port)


username = input("enter username: ")
client.send_message([1, username])
time.sleep(5)
client.send_message([1, f"hello from {username}"])
time.sleep(5)
#client.sock_io.close()
#client.sock.close()
