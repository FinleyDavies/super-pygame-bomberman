from networking import SocketServer
from game_round import GameRound
from time import sleep
from game_commands import *


def handle_message(server, message, username, round):
    if message[0] == 0:  # login message
        print("client connected")

        # send board to the new client
        server.send_message([3, str(round.get_board())], [username])

        # send all player names and ids to the new client
        server.send_to_all([0, ",".join(list(server.get_clients()))])

        server.send_message([2, f"Welcome, {username}"], [username])
        server.send_to_all([2, f"{username} has connected"], [username])


    elif message[0] == 1:   # game command message
        #print("handling", message[1])
        server.send_to_all([1, message[1]], [username])
        # add message to game queue
        # send message to all other clients except the sender


    elif message[0] == 2:   # chat message
        server.send_to_all([2, message[1]], [username])


    elif message[0] == 3:   # board file message
        pass


def add_command(server, round, command):
    # adds the command to round queue and also sends the command to all players
    round.command_queue.put(command)
    server.send_to_all([1, command.serialize()])#

def on_disconnect(server, username):
    server.send_to_all([0, ",".join(list(server.get_clients()))], [username])
    server.send_to_all([2, f"{username} has disconnected"], [username])

def main():
    server = SocketServer(on_disconnect)
    print(server.host)
    print(server.port)

    server.start_listening()

    round = GameRound("8players_1.txt")

    while True:
        for message, user in server.collect_messages():
            handle_message(server, message, user, round)
        sleep(1/60)

if __name__ == "__main__":
    main()

