class GameRound:
    GAME_LENGTH = 60 * 2
    WARMUP_LENGTH = 30

    def __init__(self):
        self.players = []
        self.spectators = []
        self.board = None
        self.warmup = False
        self.over = False
        self.min_players = 2
        self.max_players = 4

    def add_player(self, name):
        if len(self.players) > self.max_players:
            pass
