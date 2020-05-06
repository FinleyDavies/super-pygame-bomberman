import os
import pygame

from sprite import SpriteSheet, Animation
from player import Player, Bomb
from board import Board
from command import *

SPRITES_FOLDER = "Super_Bomberman_SNES"
BOARD = "Arena1.txt"
WIDTH, HEIGHT = (15 * 16 * 3, 13 * 16 * 3)
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


def main():
	pygame.init()
	screen = pygame.display.set_mode((WIDTH, HEIGHT))
	clock = pygame.time.Clock()

	sprites = load_sprites(SPRITES_FOLDER)
	player_animations = create_animations(*sprites)

	board = load_board(BOARD, (WIDTH, HEIGHT))
	player = Player(board, "player1")
	# player2 = Player(board,

	command_queue = []

	running = True
	while running:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False
			if event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
				keystate = [pygame.key.get_pressed()[key] for key in KEYS]
				command = get_command_from_keystate(keystate, player)
				command_queue.append(command)
				# client.send_command(command)

		player.update_pos()

		pygame.display.update()
		screen.fill((16, 120, 48))
		clock.tick(60)

	pygame.quit()


if __name__ == "__main__":
	main()
