from networking import SocketClient
from game_commands import Move
import time
from random import randint as ran
import player
import board
import os
import threading

host = "192.168.1.32"  # input("host: ")
port = 4832  # int(input("port: "))

username = input("enter username: ")

client = SocketClient(host, port, username)
username = client.get_username()


path = os.path.abspath(os.path.join("..", "Boards", "Arena2.txt"))
board = board.Board(open(path, "r"), "board")


def input_callback(input):
    client.send_message([2, input])


def input_thread(callback, username):
    while True:
        message = input()
        callback(f"{username}: {message}")


client.send_message([0, username])
player1 = player.Player(board, username, username)
threading.Thread(target=input_thread, args=(input_callback, username)).start()
while True:
    while not client.empty():
        client.receive_message()
    time.sleep(1/60)
