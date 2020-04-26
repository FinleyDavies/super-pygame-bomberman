import pygame
import time
import sys
import os
pygame.display.set_mode((1,1), pygame.NOFRAME)

SPRITES = "Super_Bomberman_SNES"
SCALE_FACTOR = 3
COLOUR_KEY = (16, 120, 48)

# player spritesheet dimensions:
# 16x24 pixel sprites
# 21 columns by 4 rows
players_path = os.path.join("Sprites", SPRITES, "players")
powerups_path = os.path.join("Sprites", SPRITES, "powerups")
tiles_path = os.path.join("Sprites", SPRITES, "tiles")


class SpriteSheet:
	def __init__(self, image_path, sprite_size):

		try:
			sheet = pygame.image.load(image_path)

		except pygame.error as e:
			print(f"{e}\nPlease ensure {SPRITES} is in the sprites folder")
			pygame.quit()
			sys.exit()

		width, height = sheet.get_size()
		x, y = sprite_size[0], sprite_size[1]
		cols = width // x
		rows = height // y

		sprites = [[None for _ in range(cols)] for _ in range(rows)]

		for i in range(cols):
			for j in range(rows):
				sprite = pygame.Surface(sprite_size)
				rect = pygame.Rect((i*x, j*y), sprite_size)
				sprite.blit(sheet, (0, 0), rect)
				sprite.set_colorkey(COLOUR_KEY, pygame.RLEACCEL)
				sprite = pygame.transform.scale(sprite, (x*SCALE_FACTOR, y*SCALE_FACTOR))
				sprites[j][i] = sprite

		self.sprites = sprites
		self.rows = rows
		self.cols = cols

	def get_sprites(self):
		return self.sprites

	def convert(self):
		"""
		:return: None
		surface.convert() can only be called once display has been initialised, so it must be called in main game
		before the loop.
		"""
		for i, row in enumerate(self.sprites):
			for j, sprite in enumerate(row):
				self.sprites[i][j] = sprite.convert()


class Animation:
	def __init__(self, indices, delays, sprite_sheet, loop=True):
		"""
		:list frames: list of 2d indices pointing to surfaces in a SpriteSheet object
		:list delays: duration of each frame in ms
		:bool loop: whether to play the animation once or loop it
		:SpriteSheet sprite_sheet: the sheet to get the animation frames from
		"""
		self.sprite_sheet = sprite_sheet
		self.indices = indices
		self.delays = delays
		self.duration = sum(delays)
		self.loop = loop
		self.timer = 0

	def start_animation(self):
		"""
		:return: None
		Allows animation to consistently start on the same frame each time.
		"""
		self.timer = time.time()

	def get_frame(self):
		delta = time.time() - self.timer
		delta *= 1000

		if self.loop:
			delta %= self.duration

		if delta > self.duration:
			return None

		current_frame = 0
		delay_sum = 0
		while True:
			delay_sum += self.delays[current_frame]
			if delay_sum > delta:
				break
			current_frame += 1

		return self._get_sprite(self.indices[current_frame])

	def _get_sprite(self, index):
		return self.sprite_sheet.get_sprites()[index[1]][index[0]]


path = os.path.abspath(os.path.join("..", "Sprites", SPRITES, "players.png"))
players = SpriteSheet(path, (16, 24))
walk1 = Animation([(7, 0), (6, 0), (8, 0), (6, 0)], [300, 200, 300, 200], players)
