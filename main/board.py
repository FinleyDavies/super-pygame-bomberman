import json
from command import UpdateTile


class Board:
	tiles = json.load(open("tiles.json", "r"))
	supported_symbols = [value["symbol"] for value in tiles.values()]

	def __init__(self, path, window_size):
		self.board = self._load_file(path)
		self.width, self.height = window_size
		self.rows = len(self.board)
		self.cols = len(self.board[0])

		self.tile_width = self.width // self.cols
		self.tile_height = self.height // self.rows

	def _load_file(self, path):
		board = []
		with open(path, "r") as board_file:
			for line in board_file:
				row = []
				for char in line.strip():
					if char in self.supported_symbols:
						for name, attributes in self.tiles.items():
							if attributes["symbol"] == char:
								row.append(name)
								break

					row.append(Board.tiles["floor"]["id"])

				board.append(row)

		return board

	def set_tile(self, pos, tile):
		pass

	def tile_is_occupied(self, pos):
		pass

	def get_tile_properties(self, pos):
		return self.tiles[self.board[pos[1]][pos[0]]]

	def get_updates(self):
		"""
		returns list of all tile updates for use of the graphical display
		:return:
		"""
		pass
