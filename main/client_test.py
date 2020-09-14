from networking import SocketClient, get_ip
from game_commands import *
import time
from random import randint as ran
from player import Player, Bomb
from board import Board
import os
import threading
import pygame
from queue import Queue
from collections import OrderedDict


def handle_message(client, message):
    if message[0] == 0:  # another player has connected to the server
        print("client connected")

    elif message[0] == 1:  # game command message
        print("handling", message[1])

    elif message[0] == 2:
        print(message[1])

    elif message[0] == 3:
        print(message[1])


def draw_board(surface, board):
    # draws board to game surface before drawing to screen - so the game can be offset to allow space for HUD

    colour_dic = {"floor": (16, 120, 48), "barrier": (64, 64, 64), "wall": (128, 128, 128)}
    board_size = board.get_size()
    tile_size = board.get_tile_size()

    for x in range(board_size[0]):
        for y in range(board_size[1]):
            tile = board.tile_properties((x, y))["name"]
            w, h = board.get_tile_size()
            colour = colour_dic[tile]
            pygame.draw.rect(surface, colour, pygame.Rect(x * w, y * h, w, h))

    for player in board.players:
        x, y = player.get_tile_pos()
        w, h = board.get_tile_size()
        pygame.draw.rect(surface, (0, 104, 32), pygame.Rect(x * w, y * h, w, h))

    return surface

def draw_player(surface, player):
    x, y = player.get_pos()
    w, h = player.get_size()
    rect = pygame.Rect(x, y, w, h).move(-w // 2, -h // 2)

    pygame.draw.rect(surface, player.get_colour(), rect)
    pos = player.get_pos()
    line_end = pos[0] + player.MOVEMENT_VECTORS[player.movement_direction][0] * player.width // 2, \
               pos[1] + player.MOVEMENT_VECTORS[player.movement_direction][1] * player.height // 2
    pygame.draw.line(surface, (232, 32, 32), pos, line_end, 2)
    return surface


def input_callback(client, input):
    client.send_message([2, input])


def input_thread(client, callback, username):
    while True:
        message = input()
        callback(client, f"{username}: {message}")


def get_command_from_keystate(keystate, player):
    if keystate[0]:
        if keystate[1]:
            return Move(player, 1)

        if keystate[3]:
            return Move(player, 7)

        return Move(player, 0)

    elif keystate[1]:
        if keystate[2]:
            return Move(player, 3)

        return Move(player, 2)

    elif keystate[2]:
        if keystate[3]:
            return Move(player, 5)

        return Move(player, 4)

    elif keystate[3]:
        return Move(player, 6)

    return Stop(player)


def connect(host=None, port=None, username=None):
    # returns the clients player object, the client, the board, and already connected players

    host = get_ip() if host is None else host
    port = 4832 if port is None else port
    username = "player" if username is None else username
    client = SocketClient(host, port, username)
    username = client.get_username()
    client.send_message([0, username])

    return client, username


def main():
    pygame.init()
    WIDTH, HEIGHT = (15 * 16 * 3, 13 * 16 * 3)
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    client, username = connect(host = "192.168.1.32")
    game_board = None
    player_names = []
    players = OrderedDict()
    client_player = None

    game_queue = Queue()

    KEYS = [pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d]

    threading.Thread(target=input_thread, args=(client, input_callback, username)).start()

    warmup = True
    while True:
        for message in client.collect_messages():
            if message[0] == 0:  # another player has connected to the server
                print(f"{message[1]} connected")
                player_names.append(message[1])

            elif message[0] == 1:  # game command message
                # print("handling", message[1])
                game_queue.put(deserialize(message[1], players))

                # add message to game queue

            elif message[0] == 2:   # chat
                print(message[1])

            elif message[0] == 3:   # board
                print("loaded board")
                game_board = Board.from_string(message[1])

        if game_board is None:
            continue



        for n, player in enumerate(player_names):
            p = Player(game_board, player, n)
            print(player, n)
            if player == username:
                print(client_player)
                client_player = p
            players[player] = p

        player_names = []


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
                keystate = [pygame.key.get_pressed()[key] for key in KEYS]
                command = get_command_from_keystate(keystate, client_player)
                game_queue.put(command)
                client.send_message([1, command.serialize()])


        while not game_queue.empty():
            command = game_queue.get()
            command.execute()

        board_surface = pygame.Surface((WIDTH, HEIGHT))
        board_surface = draw_board(board_surface, game_board)
        for player in players.values():
            player.update_pos()
            board_surface = draw_player(board_surface, player)

        screen.blit(board_surface, (0, 0))

        pygame.display.update()
        screen.fill((16, 120, 48))
        clock.tick(60)



if __name__ == "__main__":
    main()
