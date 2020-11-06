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
from drawing import draw_player, draw_board, convert_sheets


def handle_message(client, message):
    if message[0] == 0:  # another player has connected to the server
        print("client connected")

    elif message[0] == 1:  # game command message
        print("handling", message[1])

    elif message[0] == 2:
        print(message[1])

    elif message[0] == 3:
        return Board.from_string(client.receive_message()[1])


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


    host = input("Enter host IP (leave blank for localhost): ")
    if host == "":
        host = None

    #host = "3.17.188.254"
    client, username, game_board, players = connect(host=host, port=4832)


    client_player = players[username]

    WIDTH, HEIGHT = game_board.get_dimensions()
    print(WIDTH, HEIGHT)
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    font = pygame.font.SysFont("Arial", 50)

    def update_fps():
        fps = str(int(clock.get_fps()))
        fps_text = font.render(fps, 1, pygame.Color("green"))
        return fps_text

    menu = Menu(screen)
    # controls = Menu(screen, "Controls")
    controls = ControlsMenu(screen, ["Player1", "Player2", "Player3"], ControlsMenu.CONTROLS)
    menu.add_menu(controls)
    menu.add_button("Exit Game", lambda: pygame.event.post(pygame.event.Event(pygame.QUIT, dict())))
    menus = [menu, controls]

    actions = {
        "up": {
            True: UpdateDirection(client_player, 0, True),
            False: UpdateDirection(client_player, 0, False)
        },
        "left": {
            True: UpdateDirection(client_player, 2, True),
            False: UpdateDirection(client_player, 2, False)
        },
        "down": {
            True: UpdateDirection(client_player, 4, True),
            False: UpdateDirection(client_player, 4, False)
        },
        "right": {
            True: UpdateDirection(client_player, 6, True),
            False: UpdateDirection(client_player, 6, False)
        },
        "place bomb": {
            True: PlaceBomb(client_player),
            False: Dummy()
        },
        "punch": {
            True: Punch(client_player),
            False: Dummy()
        },
        "detonate": {
            True: Dummy(),
            False: Dummy()
        },
    }

    game_queue = Queue()

    KEYS = [pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d]

    t = threading.Thread(target=input_thread, args=(client, input_callback, username), name="client chat input")
    t.setDaemon(True)
    t.start()
    convert_sheets()

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
                print(command)
                client.send_message([1, command.serialize()])

                command = SetPosition(client_player, client_player.x, client_player.y)
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


        game_board.update()
        board_surface = draw_board(game_board)


        for player in players.values():
            player.update()
            board_surface = draw_player(board_surface, player)

        board_surface = pygame.transform.scale(board_surface, (WIDTH, HEIGHT))

        screen.blit(board_surface, (0, 0))
        screen.blit(update_fps(), (10, 0))
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
