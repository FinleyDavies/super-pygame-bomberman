# contains instances of game objects, updating based on client input, and sends updates back to clients
from networking import SocketServer
import pickle
import board
import player
import game_commands
import game_round

import random
import time
import os


CPS = 60


def handle_messages(server, game:game_round.GameRound):
    for message, user in server.collect_messages():

        if message[0] == 0:  # on connection, alert all players in chat, send all game objects to player
            server.send_to_all([1, f"{user} has connected"], [user])
            server.send_message([1, f"Welcome, {user}"], user)

            server.send_message([3, game.board.string])
            game.a

        elif message[0] == 1:
            server.send_to_all(message, [user])

        elif message[0] == 2:
            pass


def main():
    actual_cps = 0

    server = SocketServer()
    server.start_listening()

    game_objects = list()

    roll_over = 0
    cycles_elapsed = 0
    while True:
        start_time = time.time()



        # ---- CYCLE TIMING LOGIC --------------------------------------------------
        time_delta = time.time() - start_time
        sleep_time = 1 / CPS - time_delta - roll_over
        if sleep_time > 0:
            time.sleep(sleep_time)
        else:
            roll_over = abs(sleep_time)
        cycles_elapsed += 1
        actual_cps = cycles_elapsed / server.get_uptime()

if __name__ == "__main__":
    main()
