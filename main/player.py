import time


class Player:
	MOVEMENT_VECTORS = [
		[0, -1], [-1, -1], [-1, 0], [-1, 1],
		[0, 1], [1, 1], [1, 0], [1, -1],
	]

	PUNCH_TIME = 500
	CORNER_THRESH = 0.5 + 0.35

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
			# move player
			# get all surrounding movement blocking tiles
			# check for Rect collision
			# check if player in "middle row" based on movement
			# if in center, push away from tile
			# if on edge, push to the right/left of the tile

			def move(direction):
				self.x += self.MOVEMENT_VECTORS[direction % 8][0] * self.speed
				self.y += self.MOVEMENT_VECTORS[direction % 8][1] * self.speed

			move(self.direction)

			tile_position = self.board.get_pos_in_tile((self.x, self.y))
			index = self.board.get_index_from_pos((self.x, self.y))

			# TRY 1:
			# if self.MOVEMENT_VECTORS[self.direction][0] != 0:
			# 	if abs(tile_position[0]) < self.CORNER_THRESH:
			# 		pass

			# TRY 2:
			# handle directly adjacent tiles:

			# for adjacent in self.MOVEMENT_VECTORS[::2]:
			# 	shifted = index[0] + adjacent[0], index[1] + adjacent[1]
			# 	tile = self.board.tile_properties(shifted)
			#
			# 	if not tile["blocks_movement"] or :
			# 		return 0
			#
			# 	if self.MOVEMENT_VECTORS[self.direction][0] != 0:
			#
			# 		if abs(tile_position[0]) < self.CORNER_THRESH:  # if in center of tile
			# 			move(self.direction + 4)  # move opposite to direction
			#
			# 		elif tile_position > 0:  # if in top of tile
			# 			move(0)  # move up
			#
			# 		elif tile_position < 0:
			# 			move(4)  # move down

			# handle diagonal tiles:

			# TRY 3:
			# for the 3 tiles in front of player
			# check if it blocks movement
			# check whether player is colliding with line
			# get left/right offset of tiles
			# if |offset| < 1 then collision is true
			# if |offset| < CORNER_THRESH then simply move backwards
			# if offset < thresh and 2 spaces are free to left of tile, push to left
			# if offset > thresh and 2 spaces free to right, push to right
			# else push backwards

			# TRY 4:
			# check whether player is colliding with line in front
			# for each of 3 tiles:
			# get offset
			# if |offset| < 1
			# if offset < thresh and tiles to left are free
			# push to left
			# elif offset > thresh and tiles to right free
			# push to right
			# else push backwards

			dx = self.MOVEMENT_VECTORS[self.direction][0]
			if dx * tile_position[0] > 0:  # if it is colliding with wall in movement direction
				collision_candidates = [self.board.tile_properties((index[0] + i, index[1] + dx)) for i in range(3)]
				for dy in range(-1, 2):
					new_index = index[0] + dx, index[1] + dy

					up_tile = self.board.tile_properties((new_index[0], new_index[1] - 1))
					tile = self.board.tile_properties(new_index)
					down_tile = self.board.tile_properties((new_index[0], new_index[1] + 1))

					if tile["blocks_movement"]:
						offset_y = self.y - self.board.get_pos_from_index(new_index)[1]
						if abs(offset_y) < 1:
							if abs(offset_y) > self.CORNER_THRESH:
								if offset_y < 0 and up_tile["blocks_movement"] is False:
									move(0)
								elif offset_y > 0 and down_tile["blocks_movement"] is False:
									move(4)
								else:
									move(self.direction + 4)
							else:
								move(self.direction + 4)



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
		tile_x, tile_y = self.owner.board.get_index_from_pos((self.x, self.y))
		self.owner.board.create_explosion((tile_x, tile_y))
