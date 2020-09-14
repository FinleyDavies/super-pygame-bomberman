import json
from game_commands import UpdateTile
from io import StringIO
import os
from random import randint as ran


class Board:
    tiles = json.load(open("tiles.json", "r"))
    supported_symbols = [value["symbol"] for value in tiles.values()]
    SPAWN_CHAR = 'X'

    def __init__(self, board_file, board_name, window_size=None):
        self.players = []
        self.spawn_points = list()
        self.string = ""
        self.board = self._load_file(board_file)
        self.rows = len(self.board)
        self.cols = len(self.board[0])
        if window_size is None:
            window_size = self.cols * 48, self.rows * 48
        self.width, self.height = window_size
        self.board_name = board_name

        self.tile_width = self.width // self.cols
        self.tile_height = self.height // self.rows

        self.commands = []
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
        board_file = StringIO(self.string)
        board = []
        for y, line in enumerate(board_file):
            row = []
            for x, char in enumerate(line.strip()):
                if char in self.supported_symbols:
                    for name, attributes in self.tiles.items():
                        if attributes["symbol"] == char:
                            row.append(name)
                            break
                else:
                    if char == self.SPAWN_CHAR:
                        self.spawn_points.append((x, y))
                    row.append(Board.tiles["floor"]["name"])

            board.append(row)

        return board

    def create_explosion(self, index, radius):
        radius += 1

        if self.explode_tile(index):
            return 0

        for direction in [(0, 1), (-1, 0), (0, -1), (1, 0)]:
            for i in range(1, radius):  # do not include original index to prevent repeats
                offset_x, offset_y = direction
                offset_x *= i
                offset_y *= i
                new_index = index[0] + offset_x, index[1] + offset_y

                if self.explode_tile(new_index):
                    break

    def explode_tile(self, index):
        tile = self.tile_properties(index)
        if tile["is_solid"]:
            if tile["destructible"]:
                self.commands.append(UpdateTile(self, index, "flame"))
            return True
        self.commands.append(UpdateTile(self, index, "flame"))
        return False

    def update_bomb_positions(self):
        # Bombs are both tiles and objects
        bomb_positions = [(bomb.x, bomb.y) for player in self.players for bomb in player.bombs]
        print(bomb_positions)

    def set_tile(self, index, tile):
        self.board[index[1]][index[0]] = tile

    def set_tile_by_name(self, index, tile_name):
        self.board[index[1]][index[0]] = self.tiles[tile_name]["name"]

    def tile_is_occupied(self, index):
        pass

    def get_max_players(self):
        return len(self.spawn_points)

    def get_index_from_pos(self, pos):
        return pos[0] // self.tile_width, pos[1] // self.tile_height

    def get_pos_from_index(self, index):
        return (index[0] + 0.5) * self.tile_width, (index[1] + 0.5) * self.tile_height

    def get_pos_in_tile(self, pos):
        return (pos[0] % self.tile_width) / self.tile_width - 0.5, (pos[1] % self.tile_height) / self.tile_height - 0.5

    def tile_properties(self, index):
        if 0 < index[0] < self.cols and 0 < index[1] < self.rows:
            return self.tiles[self.board[index[1]][index[0]]]
        return self.tiles["barrier"]

    def get_tile_size(self):
        return self.tile_width, self.tile_height

    def get_size(self):
        return self.cols, self.rows

    def add_player(self, player):
        self.players.append(player)

    def get_updates(self):
        commands = self.commands[:]
        self.commands = []
        return commands

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
            print(board.tiles[tile]["symbol"], end="")
        print()

    board.create_explosion((2, 1), 3)
    for command in board.commands:
        print(command.index, command.tile)
        command.execute()

    for row in board.board:
        for tile in row:
            print(board.tiles[tile]["symbol"], end="")
        print()
