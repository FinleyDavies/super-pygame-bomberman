from networking import SocketServer
from game_round import GameRound
import time


def handle_message(server, message, username):
    if message[0] == 0:  # login message
        print("client connected")
        server.send_message([0, username], [username])
        server.send_to_all([2, f"{username} has connected"], [username])

    elif message[0] == 1:  # game command message
        print("handling", message[1])

    elif message[0] == 2:
        server.send_to_all([2, message[1]], [username])


def main():
    server = SocketServer()
    print(server.host)

    server.start_listening()

    round = GameRound(server, )

    while True:
        for message, user in server.collect_messages():
            handle_message(server, message, user)
        time.sleep(1/60)
