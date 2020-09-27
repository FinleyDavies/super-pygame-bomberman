from networking import SocketClient, get_ip
from game_commands import *
import time
from random import randint as ran
from player_new import Player, Bomb
from board import Board
import os
import threading
import pygame
from queue import Queue
from collections import OrderedDict
from menu import Menu, ControlsMenu


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

    colour_dic = {"floor": (16, 120, 48), "barrier": (64, 64, 64), "wall": (128, 128, 128), "flame": (207, 53, 46),
                  "wall_destroyed": (100, 100, 100)}
    board_size = board.get_size()
    tile_size = board.get_tile_size()
    #print(tile_size, board.get_tile_size_float())

    for x in range(board_size[0]):
        for y in range(board_size[1]):
            tile = board.tile_properties((x, y))["name"]
            w, h = board.get_tile_size()
            colour = colour_dic[tile]
            pygame.draw.rect(surface, colour, pygame.Rect(x * w, y * h, w, h))

    # for player in board.players.values():
    #     x, y = player.get_tile_pos()
    #     w, h = board.get_tile_size()
    #     pygame.draw.rect(surface, (0, 104, 32), pygame.Rect(x * w, y * h, w, h))

    # for coord in board.flames:
    #     x, y = coord
    #     w, h = board.get_tile_size()
    #     pygame.draw.rect(surface, (207, 53, 46), pygame.Rect(x * w, y * h, w, h))


    return surface

def draw_player(surface, player):
    x, y = player.get_pos()
    w, h = player.get_size()
    rect = pygame.Rect(x, y, w, h).move(-w // 2, -h // 2)

    pygame.draw.rect(surface, player.get_colour(), rect)
    pos = player.get_pos()
    line_end = pos[0] + player.MOVEMENT_VECTORS[player.movement_direction][0] * player.width // 2, \
               pos[1] + player.MOVEMENT_VECTORS[player.movement_direction][1] * player.height // 2
    pygame.draw.line(surface, (32, 32, 32), pos, line_end, 2)

    for bomb in player.get_bombs():
        x, y = bomb.get_pos()
        w, h = player.get_size()
        w, h = w - 20, h - 20
        rect = pygame.Rect(x, y, w, h).move(-w // 2, -h // 2)
        pygame.draw.rect(surface, (50, 50, 50), rect)

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

def load_players(names, board):
    print("Loading players")

    players = OrderedDict()
    for i, name in enumerate(names):
        print(f"\t{name} ({i + 1})")
        players[name] = (Player(board, name, i))

    print("\nSuccessfully loaded players\n\n")

    return players

def connect(host=None, port=None, username=None):
    # returns the clients player object, the client, the board, and already connected players

    host = get_ip() if host is None else host
    port = 4832 if port is None else port
    username = "player" if username is None else username

    print(f"Connecting to server {host} on port {port} with username {username}")
    client = SocketClient(host, port, username)
    username = client.get_username()
    print(f"successfully connected with username {username}\n")

    client.send_message([0, username])

    print("Loading board")
    game_board = Board.from_string(client.receive_message()[1])
    print(game_board)
    print("Game board has been loaded\n")

    names = client.receive_message()[1].split(",")
    players = load_players(names, game_board)

    return client, username, game_board, players


def main():
    pygame.init()

    while True:
        host = input("Enter host IP (leave blank for localhost): ")
        if host == "":
            host = None
        try:
            client, username, game_board, players = connect(host=host)
            break
        except:
            print("invalid IP address")

    client_player = players[username]

    WIDTH, HEIGHT = game_board.get_dimensions()
    print(WIDTH, HEIGHT)
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    menu = Menu(screen)
    # controls = Menu(screen, "Controls")
    controls = ControlsMenu(screen, ["Player1", "Player2", "Player3"])
    menu.add_menu(controls)
    menu.add_button("Exit Game", lambda: pygame.event.post(pygame.event.Event(pygame.QUIT, dict())))
    menus = [menu, controls]

    game_queue = Queue()

    KEYS = [pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d]

    t = threading.Thread(target=input_thread, args=(client, input_callback, username), name="client chat input")
    t.setDaemon(True)
    t.start()

    times_test = []
    warmup = True
    running = True
    while running:
        for message in client.collect_messages():

            if message[0] == 0:     # reset player list
                names = message[1].split(",")
                game_board.clear_players()
                players = load_players(names, game_board)
                client_player = players[username]

            elif message[0] == 1:   # game command
                objects = players.copy()
                objects[game_board.get_id()] = game_board
                game_queue.put(deserialize(message[1], objects))

            elif message[0] == 2:   # chat message
                print(message[1])

            elif message[0] == 3:   # board update
                print("loaded board")
                game_board = Board.from_string(message[1])

            elif message[0] == 4:   # remove player
                del players[message[1]]

            elif message[0] == 5:   # add player
                name, id  = message[1].split(",")



        for event in pygame.event.get():
            [menu.update(event) for menu in menus]

            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
                keystate = [pygame.key.get_pressed()[key] for key in KEYS]
                command = get_command_from_keystate(keystate, client_player)
                game_queue.put(command)
                client.send_message([1, command.serialize()])

                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    # command = CreateExplosion(game_board, client_player.get_tile_pos(), 4)
                    command = PlaceBomb(client_player)
                    game_queue.put(command)
                    client.send_message([1, command.serialize()])


        while not game_queue.empty():
            command = game_queue.get()
            command.execute()

        board_surface = pygame.Surface((WIDTH, HEIGHT))
        game_board.update()
        board_surface = draw_board(board_surface, game_board)


        for player in players.values():
            player.update()
            board_surface = draw_player(board_surface, player)

        screen.blit(board_surface, (0, 0))
        [menu.draw() for menu in menus]
        pygame.display.update()
        screen.fill((16, 120, 48))
        clock.tick(60)

    print("broken")
    client.close()
    print("CLOSED")
    pygame.quit()
    print("QUIT")


if __name__ == "__main__":
    main()
