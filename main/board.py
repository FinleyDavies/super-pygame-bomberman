import json
from game_commands import UpdateTile
from io import StringIO
import os
from random import randint as ran
from collections import OrderedDict
from tile import Tile
from time import time


class Board:
    SPAWN_CHAR = 'X'

    def __init__(self, board_file, board_name, window_size=None):
        self.players = OrderedDict()
        self.spawn_points = list()
        self.string = ""
        self._load_file(board_file)

        self.rows = len(self.board)
        self.cols = len(self.board[0])
        if window_size is None:
            window_size = self.cols * 32, self.rows * 32

        self.width, self.height = window_size
        self.board_name = board_name

        self.tile_width = self.width // self.cols
        self.tile_height = self.height // self.rows
        self.tile_width_float = self.width / self.cols
        self.tile_height_float = self.height / self.rows

        # print(self.spawn_points)

    @classmethod
    def from_file_name(cls, board_name, window_size=None):
        path = os.path.abspath(os.path.join("..", "Boards", board_name))
        board_file = open(path, "r")
        board_name = board_name.replace(".txt", "")
        return cls(board_file, board_name, window_size)

    @classmethod
    def from_string(cls, board_string, window_size=None):
        board_file = StringIO(board_string)
        return cls(board_file, "game_board", window_size)

    def _load_file(self, board_file):
        self.string = board_file.read()
        self.board = [[Tile() for _ in range(len(line))] for line in self.string.split()]

        board_file = StringIO(self.string)
        for y, line in enumerate(board_file):
            for x, char in enumerate(line.strip()):
                if char in Tile.supported_symbols:
                    for name, attributes in Tile.tile_properties.items():
                        if attributes["symbol"] == char:
                            self.set_tile((x, y), name)
                            break

                elif char == self.SPAWN_CHAR:
                    self.spawn_points.append((x, y))
                    self.set_tile((x, y), "floor")

    def create_explosion(self, index, radius):
        print("explosion")
        radius += 1

        if self.board[index[1]][index[0]].explode():
            return 0

        for direction in [(0, 1), (-1, 0), (0, -1), (1, 0)]:
            for i in range(1, radius):  # do not include original index to prevent repeats
                offset_x, offset_y = direction
                offset_x *= i
                offset_y *= i
                new_index = index[0] + offset_x, index[1] + offset_y

                if self.board[new_index[1]][new_index[0]].explode():
                    break

    def update(self):
        for row in self.board:
            for tile in row:
                tile.update()

    def update_bomb_positions(self):
        # Bombs are both tiles and objects
        bomb_positions = [(bomb.x, bomb.y) for player in self.players.values() for bomb in player.bombs]
        print(bomb_positions)

    def set_tile(self, index, tile_name):
        self.board[index[1]][index[0]].set_tile(tile_name)

    def tile_is_occupied(self, index):
        pass

    def get_max_players(self):
        return len(self.spawn_points)

    def get_index_from_pos(self, pos):
        return int(pos[0] // self.tile_width), int(pos[1] // self.tile_height)

    def get_pos_from_index(self, index):
        return (index[0] + 0.5) * self.tile_width, (index[1] + 0.5) * self.tile_height

    def get_pos_in_tile(self, pos):
        return (pos[0] % self.tile_width) / self.tile_width - 0.5, (pos[1] % self.tile_height) / self.tile_height - 0.5

    def tile_properties(self, index):
        if 0 < index[0] < self.cols and 0 < index[1] < self.rows:
            return self.board[index[1]][index[0]]
        return Tile.new_tile("barrier")

    def get_tile_size(self):
        return self.tile_width, self.tile_height

    def get_tile_size_float(self):
        return self.tile_width_float, self.tile_height_float

    def get_size(self):
        return self.cols, self.rows

    def get_dimensions(self):
        return self.width, self.height

    def add_player(self, player):
        self.players[player.player_name] = player

    def clear_players(self):
        self.players = OrderedDict()

    def get_id(self):
        return self.board_name

    def __str__(self):
        return self.string


if __name__ == "__main__":

    BOARD = "Arena1.txt"
    WIDTH, HEIGHT = (15 * 16 * 3, 13 * 16 * 3)


    def load_board(file_name, board_name, size):
        path = os.path.abspath(os.path.join("..", "Boards", file_name))
        file = open(path, "r")
        return Board(file, board_name, size)


    board = Board.from_file_name("Arena1.txt", (WIDTH, HEIGHT))

    for row in board.board:
        for tile in row:
            print(tile["symbol"], end="")
        print()

    board.create_explosion((1, 1), 3)

    for row in board.board:
        for tile in row:
            print(tile["symbol"], end="")
        print()
