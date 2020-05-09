import os
import pygame

from sprite import SpriteSheet, Animation
from player import Player, Bomb
from board import Board
from command import *

SPRITES_FOLDER = "Super_Bomberman_SNES"
BOARD = "Arena2.txt"
WIDTH, HEIGHT = (15 * 16 * 3, 13 * 16 * 3)
#WIDTH, HEIGHT = 700, 500
KEYS = [pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d]


def load_sprites(folder):
	players_path = os.path.abspath(os.path.join("..", "Sprites", folder, "players.png"))
	tiles_path = os.path.abspath(os.path.join("..", "Sprites", folder, "tiles.png"))
	powerups_path = os.path.abspath(os.path.join("..", "Sprites", folder, "powerups.png"))

	players = SpriteSheet(players_path, (16, 24))
	tiles = SpriteSheet(tiles_path, (16, 24))
	powerups = SpriteSheet(powerups_path, (16, 24))

	return players, tiles, powerups


def load_board(board_name, size):
	path = os.path.abspath(os.path.join("..", "Boards", board_name))
	return Board(path, size)


def create_animations(players, tiles, powerups):
	player_animations = dict()
	for i, colour in enumerate(["white", "blue", "black", "red"]):
		player_animations["colour"] = dict()

		walk = list()
		walking_delays = [300, 200, 300, 200]
		for j in range(4):
			j *= 3
			sequence = [(j + 1, i), (j, i), (j + 2, i), (j, i)]
			animation = Animation(players, sequence, walking_delays)
			walk.append(animation)

		punch = list()
		for j in range(4):
			j += 19
			animation = Animation(players, [(j, i)], 500, False)
			punch.append(animation)

		death = Animation(players, [(j, i) for j in range(12, 18)], 2000, False)

		player_animations["colour"]["walk"] = walk
		player_animations["colour"]["punch"] = punch
		player_animations["colour"]["death"] = death

	return player_animations


def get_command_from_keystate(keystate, player):
	if keystate[0]:
		if keystate[1]:
			return Move(player, 1)

		if keystate[3]:
			return Move(player, 7)

		return Move(player, 0)

	elif keystate[1]:
		if keystate[2]:
			return Move(player, 3)

		return Move(player, 2)

	elif keystate[2]:
		if keystate[3]:
			return Move(player, 5)

		return Move(player, 4)

	elif keystate[3]:
		return Move(player, 6)

	return Stop(player)


def draw_board(surface, board):
	# draws board to game surface before drawing to screen - so the game can be offset to allow space for HUD

	colour_dic = {"floor": (16, 120, 48), "barrier": (64, 64, 64), "wall": (128, 128, 128)}
	board_size = board.get_size()
	tile_size = board.get_tile_size()

	for x in range(board_size[0]):
		for y in range(board_size[1]):
			tile = board.tile_properties((x, y))["name"]
			colour = colour_dic[tile]
			pygame.draw.rect(surface, colour, board.get_tile_rect((x, y)))

	for player in board.players:
		pygame.draw.rect(surface, (0, 104, 32), board.get_tile_rect(player.get_tile_pos()))

	return surface


def draw_grid(surface, board):
	board_size = board.get_size()
	tile_size = board.get_tile_size()

	for x in range(1, board_size[0]):
		x *= tile_size[0]
		pygame.draw.line(surface, (30, 30, 30), (x, 0), (x, surface.get_height()))

	for y in range(1, board_size[1]):
		y *= tile_size[1]
		pygame.draw.line(surface, (30, 30, 30), (0, y), (surface.get_width(), y))


def draw_player(surface, player):
	pygame.draw.rect(surface, player.get_colour(), player.get_rect())
	pos = player.get_pos()
	line_end = pos[0] + player.MOVEMENT_VECTORS[player.movement_direction][0] * player.width // 2, \
			   pos[1] + player.MOVEMENT_VECTORS[player.movement_direction][1] * player.height // 2
	pygame.draw.line(surface, (232, 32, 32), pos, line_end, 2)
	return surface


def main():
	pygame.init()
	screen = pygame.display.set_mode((WIDTH, HEIGHT))
	board_surface = pygame.Surface((WIDTH, HEIGHT))
	clock = pygame.time.Clock()

	sprites = load_sprites(SPRITES_FOLDER)
	player_animations = create_animations(*sprites)

	board = load_board(BOARD, (WIDTH, HEIGHT))
	player = Player(board, "player1")
	player.set_tile_pos((1, 1))
	# player2 = Player(board,

	command_queue = []

	running = True
	while running:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False
			if event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
				#print(player.get_pos())
				keystate = [pygame.key.get_pressed()[key] for key in KEYS]
				command = get_command_from_keystate(keystate, player)
				command_queue.append(command)
				# client.send_command(command)

		for command in command_queue:
			print(command)
			command.execute()
		command_queue = []
		player.update_pos()
		draw_board(board_surface, board)
		draw_player(board_surface, player)
		draw_grid(board_surface, board)
		screen.blit(board_surface, (0, 0))

		pygame.display.update()
		screen.fill((16, 120, 48))
		clock.tick(60)

	pygame.quit()


if __name__ == "__main__":
	main()
