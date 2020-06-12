from networking import SocketClient
from game_commands import Move
import time
from random import randint as ran
import player
import board
import os
import threading

host = "192.168.0.55"  # input("host: ")
port = 4832  # int(input("port: "))

username = input("enter username: ")
client = SocketClient(host, port, username)
username = client.get_username()


path = os.path.abspath(os.path.join("..", "Boards", "Arena2.txt"))
board = board.Board(path, (10, 10), "board")


def input_callback(input):
    client.send_message([2, input])


def input_thread(callback, username):
    while True:
        message = input()
        callback(f"{username}: {message}")


client.send_message([0, username])
player1 = player.Player(board, username)
threading.Thread(target=input_thread, args=(input_callback, username)).start()
while True:
    while not client.empty():
        print(client.receive_message()[1])
    time.sleep(1/60)
