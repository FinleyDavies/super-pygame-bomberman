from networking import SocketServer
import time

server = SocketServer()

server.start_listening()
while 1:
    message = f"({time.strftime('%H:%M:%S', time.localtime())}) hello from the server"
    server.send_to_all([1, message])
    print(f"(Game) Connected clients: {server.clients}")
    time.sleep(20)
    for client in server.clients.values():
        client["sockIO"].close()
