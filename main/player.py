import time
import os


class Player:
	MOVEMENT_VECTORS = [
		[0, -1], [-1, -1], [-1, 0], [-1, 1],
		[0, 1], [1, 1], [1, 0], [1, -1],
	]

	def __init__(self):
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

	def update_pos(self):
		if self.is_moving:
			self.x += self.MOVEMENT_VECTORS[self.direction][0] * self.speed
			self.y += self.MOVEMENT_VECTORS[self.direction][1] * self.speed

	def place_bomb(self):
		if self.bombs_active < self.bomb_count:
			self.bombs.append(Bomb(self))
			self.bomb_count += 1

	def punch(self):
		pass

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


# TODO TESTING CODE remove after full implementation
if __name__ == "__main__":
	import pygame
	import command
	from sprite import testing_anim

	pygame.init()

	WIDTH, HEIGHT = (640, 480)
	screen = pygame.display.set_mode((WIDTH, HEIGHT))

	KEYS = [pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d]

	clock = pygame.time.Clock()
	player = Player()

	def get_command_from_keystate(keystate):
		if keystate[0]:
			if keystate[1]:
				return command.Move(player, 1)
			if keystate[3]:
				return command.Move(player, 7)
			return command.Move(player, 0)

		elif keystate[1]:
			if keystate[2]:
				return command.Move(player, 3)
			return command.Move(player, 2)

		elif keystate[2]:
			if keystate[3]:
				return command.Move(player, 5)
			return command.Move(player, 4)

		elif keystate[3]:
			return command.Move(player, 6)

		return command.Stop(player)

	running = True
	while running:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False
			if event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
				testing_anim.start_animation()
				keystate = [pygame.key.get_pressed()[key] for key in KEYS]
				print(keystate)
				get_command_from_keystate(keystate).execute()
				print(player.get_direction())

		player.update_pos()
		if player.get_is_moving():
			screen.blit(testing_anim.get_current_frame(), player.get_pos())
		else:
			screen.blit(testing_anim.get_frame(1), player.get_pos())

		pygame.display.update()
		screen.fill((16, 120, 48))
		clock.tick(60)

	pygame.quit()
