import game_commands
import queue
import player
import os
import board

class GameRound:
    GAME_LENGTH = 60 * 2
    WARMUP_LENGTH = 30

    def __init__(self, board_name):
        self.players = []
        self.spectators = []
        self.board = self.load_board(board_name)
        self.warmup = False
        self.over = False
        self.min_players = 2
        self.max_players = self.board.get_max_players()
        self.command_queue = queue.Queue()

    def add_player(self, name):
        if len(self.players) < self.max_players:
            p = player.Player(self.board, name, len(self.players))
            self.players.append(p)
        else:
            self.spectators.append(name)

    def add_players(self, names):
        for name in names:
            self.add_player(name)

    def get_game_objects(self):
        return self.players + [self.board]

    def deserialise_command(self, message):
        command = game_commands.deserialize(message, self.get_game_objects())
        self.command_queue.put(command)

    def load_board(self, board_file):
        return board.Board(board_file, "game_board")
