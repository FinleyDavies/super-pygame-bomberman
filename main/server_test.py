from networking import SocketServer
import pygame
import time

server = SocketServer()

server.start_listening()
clock = pygame.time.Clock()


def handle_message(message, username):
    if message[0] == 0:  # login message
        print("client connected")
        server.send_message([0, username], username)
    elif message[0] == 1:  # game command message
        print("handling", message[1])

    elif message[0] == 2:
        pass

    print()


while True:
    # message = f"({time.strftime('%H:%M:%S', time.localtime())}) hello from the server"
    # server.send_to_all([1, message])
    # print(f"(Game) Connected clients: {server.clients}")
    for username, client in server.clients.items():
        while not client.input_empty():
            print("getting message: ", end="")
            message = client.get_input()
            print(message)
            # print(message)
            handle_message(message, username)
    clock.tick(60)
