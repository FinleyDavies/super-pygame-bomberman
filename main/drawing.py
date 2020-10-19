#import pygame
from sprite import *
import os


SPRITESIZE = [16, 16]
PLAYERSIZE = [16, 24]

PLAYER_SHEET = SpriteSheet(PLAYER_PATH, PLAYERSIZE)
TILES_SHEET = SpriteSheet(TILE_PATH, SPRITESIZE)
POWERUP_SHEET = SpriteSheet(POWERUP_PATH, SPRITESIZE)

def create_animations(players, tiles, powerups):
    # TODO remake to allow any number of colours to be added - based on spritesheet size

    colours = ["white", "blue", "black", "red"]

    # CREATE PLAYER ANIMATIONS ############################################################################
    player_animations = dict()

    for i, colour in enumerate(colours):  # for each player colour
        player_animations[colour] = dict()

        walk = list()
        walking_delays = [300, 200, 300, 200]

        stand = list()

        for j in range(4):  # for each direction
            j *= 3
            sequence = [(j + 1, i), (j, i), (j + 2, i), (j, i)]
            animation = Animation(players, sequence, walking_delays)
            walk.append(animation)

            animation = Animation(players, [(j, i)], 0)
            stand.append(animation)

        punch = list()
        for j in range(4):
            j += 19
            animation = Animation(players, [(j, i)], 500, False)
            punch.append(animation)

        death = Animation(players, [(j, i) for j in range(12, 18)], 2000, False)

        player_animations[colour]["walk"] = walk
        player_animations[colour]["stand"] = stand
        player_animations[colour]["punch"] = punch
        player_animations[colour]["death"] = death

    # CREATE TILE ANIMATIONS ##############################################################################
    tile_animations = dict()

    barrier             = Animation(tiles, [[1, 0]], 0)
    wall                = Animation(tiles, [[2, 0]], 0)
    wall_destroyed      = Animation(tiles, [[i, 3] for i in range(6)], 500)
    powerup_destroyed   = Animation(tiles, [[i, 4] for i in range(7)], 500)
    bomb                = Animation(tiles, [[0, 1], [1, 1], [2, 1], [1, 1]], 1200)
    flame               = Animation(tiles, [[i, 10] for i in range(5)], 720)

    tile_animations["barrier"] = barrier
    tile_animations["wall"] = wall
    tile_animations["wall_destroyed"] = wall_destroyed
    tile_animations["powerup_destroyed"] = powerup_destroyed
    tile_animations["bomb_entity"] = bomb
    tile_animations["flame"] = flame

    # CREATE POWERUP ANIMATIONS ###########################################################################
    powerup_animations = dict()

    return player_animations, tile_animations, powerup_animations


PLAYER_ANIMATIONS, TILE_ANIMATIONS, POWERUP_ANIMATIONS = create_animations(PLAYER_SHEET, TILES_SHEET, POWERUP_SHEET)

def convert_sheets():
    PLAYER_SHEET.convert()
    TILES_SHEET.convert()
    POWERUP_SHEET.convert()

def draw_board(board):
    # returns a surface with size


    colour_dict = {"floor": (16, 120, 48), "barrier": (64, 64, 64), "wall": (128, 128, 128), "flame": (207, 53, 46),
                   "wall_destroyed": (100, 100, 100), "spawn": (100, 110, 38), "bomb": (16, 120, 48)}

    board_size = board.get_size()
    surface = pygame.Surface((board_size[0]*SPRITESIZE[0], board_size[1]*SPRITESIZE[1]))
    surface.fill(colour_dict["floor"])

    # tile_width, tile_height = board.get_tile_size()

    for x in range(board_size[0]):
        for y in range(board_size[1]):
            tile_name = board.tile_properties((x, y))["name"]
            tile_birth = board.tile_properties((x, y))["birth"]

            if tile_name in TILE_ANIMATIONS:
                tile = TILE_ANIMATIONS[tile_name].get_current_frame(tile_birth)
                surface.blit(tile, (x * SPRITESIZE[0], y * SPRITESIZE[1]))
            else:
                colour = colour_dict[tile_name]
                pygame.draw.rect(surface, colour, pygame.Rect(x * SPRITESIZE[0], y * SPRITESIZE[1],
                                                              SPRITESIZE[0], SPRITESIZE[1]))

    # for player in board.players.values():
    #     x, y = player.get_tile_pos()
    #     w, h = board.get_tile_size()
    #     pygame.draw.rect(surface, (0, 104, 32), pygame.Rect(x * w, y * h, w, h))

    # for coord in board.flames:
    #     x, y = coord
    #     w, h = board.get_tile_size()
    #     pygame.draw.rect(surface, (207, 53, 46), pygame.Rect(x * w, y * h, w, h))

    return surface


def draw_player(surface, player):
    w, h = player.get_size()

    for bomb in player.get_bombs():
        x, y = bomb.get_pos()
        birth = bomb.time_created
        x = int(x * SPRITESIZE[0] / w)
        y = int(y * SPRITESIZE[1] / h)
        rect = pygame.Rect((x, y), SPRITESIZE).move(-SPRITESIZE[0] // 2, -SPRITESIZE[1] // 2)
        frame = TILE_ANIMATIONS["bomb_entity"].get_current_frame(birth)
        surface.blit(frame, rect)

    x, y = player.get_pos()
    x = int(x * SPRITESIZE[0] / w)
    y = int(y * SPRITESIZE[1] / h)
    pid = player.player_id
    direction = player.movement_direction
    moving = player.is_moving
    rect = pygame.Rect((x, y), PLAYERSIZE).move(-SPRITESIZE[0] // 2, SPRITESIZE[1]//2-PLAYERSIZE[1])
    frame = PLAYER_ANIMATIONS[["white", "blue", "black", "red"][pid%4]]["walk" if moving else "stand"][direction//2].get_current_frame()
    surface.blit(frame, rect)
    #pygame.draw.rect(surface, player.get_colour(), rect)


        #pygame.draw.rect(surface, (50, 50, 50), rect)

    return surface
