# contains instances of game objects, updating based on client input, and sends updates back to clients
from networking import SocketServer
import board
import player
import command

import random
import time
import os


CPS = 60
actual_cps = 0

server = SocketServer()
server.start_listening()

game_objects = list()


def load_board(board_name, size):
    path = os.path.abspath(os.path.join("..", "Boards", board_name))
    return board.Board(path, size, "game_board")


def handle_message(message, user, game_objects):
    if message[0] == 0:
        server.send_to_all([2, f"{user} has connected"], [user])
        server.send_message([2, f"Welcome, {user}"])

    elif message[0] == 2:
        server.send_to_all(message, [user])


roll_over = 0
cycles_elapsed = 0
while True:
    start_time = time.time()

    for message, user in server.collect_messages():
        handle_message(message, user, game_objects)

    # ---- CYCLE TIMING LOGIC --------------------------------------------------
    time_delta = time.time() - start_time
    sleep_time = 1 / CPS - time_delta - roll_over
    if sleep_time > 0:
        time.sleep(sleep_time)
    else:
        roll_over = abs(sleep_time)
    cycles_elapsed += 1
    actual_cps = cycles_elapsed / server.get_uptime()
