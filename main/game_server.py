# contains instances of game objects, updating based on client input, and sends updates back to clients
from networking import SocketServer


server = SocketServer

commands = []


while True:
    commands.append(server.get_commands())
    server.clear_commands()
    for command in commands:
        command.decode()
        command.execute()
        server.send_to_all(command)

