import time
import os
from abc import ABCMeta


class Player:
	MOVEMENT_VECTORS = [
		[1, 0], [1, 1], [0, 1], [-1, 1],
		[-1, 0], [-1, -1], [0, -1], [1, -1]
	]

	def __init__(self):
		self.x = 0
		self.y = 0
		self.speed = 1
		self.bomb_count = 1
		self.bomb_radius = 2
		self.bombs_active = 0
		self.bombs = []
		self.powerups = [False, False, False, False]

	def move(self, direction):
		self.x += self.MOVEMENT_VECTORS[direction][0] * self.speed
		self.y += self.MOVEMENT_VECTORS[direction][1] * self.speed

	def place_bomb(self):
		if self.bombs_active < self.bomb_count:
			self.bombs.append(Bomb(self))
			self.bomb_count += 1

	def remove_bomb(self, bomb):
		self.bombs.remove(bomb)
		self.bomb_count -= 1

	def has_remote_detonation(self):
		return self.powerups[2]

	def get_bomb_radius(self):
		return self.bomb_radius


class Bomb:
	def __init__(self, owner):
		self.time_created = time.time()
		self.owner = owner
		self.fuse_time = 2.5
		self.radius = owner.get_bomb_radius()

	def tick(self):
		delta = time.time() - self.time_created
		if delta > self.fuse_time:
			self.explode()

	def explode(self):
		self.owner.remove_bomb(self)


class Board:
	def __init__(self, path, window_size):
		self.board = []
		with open(path, "r") as board_file:
			for line in board_file:
				self.board.append([tile for tile in line.strip()])

		self.width, self.height = window_size
		self.rows = len(self.board)
		self.cols = len(self.board[0])

		self.tile_width = self.width // self.cols
		self.tile_height = self.height // self.rows

	def get_tile(self, x, y):
		pass




path = os.path.abspath(os.path.join("..", "Arenas", "Arena1.txt"))
b = Board(path)
