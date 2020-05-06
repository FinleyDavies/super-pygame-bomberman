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

		self.commands = []

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
					else:
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
				print(new_index)

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

	def set_tile(self, index, tile):
		pass

	def tile_is_occupied(self, index):
		pass

	def get_index_from_pos(self, pos):
		return pos[0] // self.tile_width, pos[1] // self.tile_height

	def tile_properties(self, index):
		print(self.board[index[1]][index[0]])
		return self.tiles[self.board[index[1]][index[0]]]

	def get_updates(self):
		"""
		returns list of all tile updates for use of the graphical display
		:return:
		"""
		pass


if __name__ == "__main__":
	import os

	BOARD = "Arena1.txt"
	WIDTH, HEIGHT = (15 * 16 * 3, 13 * 16 * 3)

	def load_board(board_name, size):
		path = os.path.abspath(os.path.join("..", "Boards", board_name))
		return Board(path, size)

	board = load_board(BOARD, (WIDTH, HEIGHT))

	for row in board.board:
		for tile in row:
			print(board.tiles[tile]["symbol"], end="")
		print()

	board.create_explosion((3, 1), 2)
	for command in board.commands:
		print(command.index, command.tile)