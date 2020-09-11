import game_commands
import queue
import player
import os
import board


# Server side class used to keep track of players and start and end games appropriately

class GameRound:
    GAME_LENGTH = 60 * 2
    WARMUP_LENGTH = 30

    def __init__(self, server, board_name):
        self.server = server
        self.players = []
        self.spectators = []
        self.board = self.load_board(board_name)
        self.warmup = False
        self.game_over = False
        self.min_players = 2
        self.max_players = self.board.get_max_players()
        self.command_queue = queue.Queue()
        self.respawns = True

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

    def update(self):
        while not self.command_queue.empty():
            self.command_queue.get().execute()

        if self.warmup:
            for player in self.get_dead_players():
                player_no = self.players.index(player)
                position = self.board.spawn_points[player_no]

                # add SetAlive command to network queue
                # add SetPosition to network queue

    def get_living_players(self):
        living = list()

        for player in self.players:
            if player.is_alive():
                living.append(player)

        return living

    def get_dead_players(self):
        living = self.get_living_players()
        return list(set(self.players) - set(living))

    def add_command(self, command):
        # adds the command to round queue and also sends the command to all players
        self.command_queue.put(command)
        self.server.send_to_all()


if __name__ == "__main__":
    board_name = "Arena1.txt"
    path = os.path.abspath(os.path.join("..", "Boards", board_name))
    BOARD = open(path, "r")

    round1 = GameRound(BOARD)
    round1.add_player("player_1")
