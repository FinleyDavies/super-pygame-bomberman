import time


class Player:
	MOVEMENT_VECTORS = [
		[0, -1], [-1, -1], [-1, 0], [-1, 1],
		[0, 1], [1, 1], [1, 0], [1, -1],
	]

	PUNCH_TIME = 500

	def __init__(self, board, player_id):
		self.player_id = player_id
		self.board = board
		self.x = 0
		self.y = 0
		self.speed = 3
		self.bomb_count = 1
		self.bomb_radius = 2
		self.bombs_active = 0
		self.bombs = []
		self.powerups = [False, False, False, False]
		self.direction = 2  # facing downwards
		self.is_moving = False
		self.time_punched = 0

	def update_pos(self):
		if self.is_moving and not self.is_punching():
			self.x += self.MOVEMENT_VECTORS[self.direction][0] * self.speed
			self.y += self.MOVEMENT_VECTORS[self.direction][1] * self.speed

	def place_bomb(self):
		if self.bombs_active < self.bomb_count:
			self.bombs.append(Bomb(self))
			self.bomb_count += 1

	def punch(self):
		self.time_punched = time.time()

	def is_punching(self):
		return (time.time() - self.time_punched * 1000) < self.PUNCH_TIME

	def remove_bomb(self, bomb):
		self.bombs.remove(bomb)
		self.bomb_count -= 1

	def has_remote_detonation(self):
		return self.powerups[2]

	def get_bomb_radius(self):
		return self.bomb_radius

	def set_direction(self, direction):
		self.direction = direction

	def set_is_moving(self, is_moving):
		self.is_moving = is_moving

	def get_direction(self):
		return self.direction

	def get_is_moving(self):
		return self.is_moving

	def get_pos(self):
		return self.x, self.y


class Bomb:
	def __init__(self, owner):
		self.time_created = time.time()
		self.owner = owner
		self.x, self.y = self.owner.get_pos()
		self.fuse_time = 2.5
		self.radius = self.owner.get_bomb_radius()

	def tick(self):
		delta = time.time() - self.time_created
		if delta > self.fuse_time:
			self.explode()

	def explode(self):
		self.owner.remove_bomb(self)
		tile_x, tile_y = self.owner.board.get_tile_from_pos((self.x, self.y))
		self.owner.board.explode_tile((tile_x, tile_y))

