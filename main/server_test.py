from networking import SocketServer
import time

server = SocketServer()

server.start_listening()
while 1:
    print(server.get_commands())
    print(server.clients)
    time.sleep(3)
