import time
from random import random, randint


class Player:
    MOVEMENT_VECTORS = [
        [0, -1], [-1, -1], [-1, 0], [-1, 1],
        [0, 1], [1, 1], [1, 0], [1, -1],
    ]

    PUNCH_TIME = 500
    CORNER_THRESH = 0.5 + 0.1

    def __init__(self, board, player_name, player_id):
        self.player_name = player_name
        self.player_id = player_id

        self.board = board
        self.board.add_player(self)
        self.width, self.height = self.board.get_tile_size()
        self.x, self.y = 0, 0
        self.is_alive = True

        self.speed = self.width // 8 // 2
        self.bomb_count = 1
        self.bomb_radius = 2
        self.bombs_active = 0
        self.bombs = []
        self.powerups = [False, False, False, False]
        self.movement_direction = 2  # facing downwards
        self.control_direction = 2
        self.is_moving = False
        self.time_punched = 0
        self.colour = (232, 232, 232)
        self.last_component = 0

    def update_pos(self):
        if self.is_moving and not self.is_punching():
            self.change_direction()

            # move player
            # get all surrounding movement blocking tiles
            # check for Rect collision
            # check if player in "middle row" based on movement
            # if in center, push away from tile
            # if on edge, push to the right/left of the tile

            def move(vector):
                self.x += vector[0] * self.speed
                self.y += vector[1] * self.speed

            vec = self.MOVEMENT_VECTORS[self.movement_direction]

            # todo fix the bug where player gets stuck on corners when moving diagonally
            #  - by using approach similar to below code, but switching component when entering a new tile, instead of
            #  every frame
            # if vec[0] != 0 and vec[1] != 0:
            # 	if self.last_component == 0:
            # 		move([vec[0], 0])
            # 	else:
            # 		move([0, vec[1]])
            # 	self.last_component = (self.last_component + 1) % 2
            # else:
            # 	move(vec)

            move(vec)

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

            # move([vec[0], 0])
            if vec[0] * tile_position[0] > 0:  # if it is colliding with wall in movement direction
                for dy in range(-1, 2):  # loop over the tiles in front
                    new_index = index[0] + vec[0], index[1] + dy

                    up_tile = self.board.tile_properties((new_index[0], new_index[1] - 1))
                    tile = self.board.tile_properties(new_index)
                    down_tile = self.board.tile_properties((new_index[0], new_index[1] + 1))

                    if tile["blocks_movement"]:
                        offset_y = self.y - self.board.get_pos_from_index(new_index)[1]
                        if abs(offset_y) < self.height - 1:
                            # print("hit x")
                            if abs(offset_y) > self.CORNER_THRESH * self.height:
                                if offset_y < 0 and up_tile["blocks_movement"] is False:
                                    # print("up", dy)
                                    move([0, -1])
                                elif offset_y > 0 and down_tile["blocks_movement"] is False:
                                    # print("down", dy)
                                    move([0, 1])
                                else:
                                    move([-vec[0], 0])
                            else:
                                move([-vec[0], 0])
                            break

            # move([0, vec[1]])
            if vec[1] * tile_position[1] > 0:  # if it is colliding with wall in movement direction
                for dx in range(-1, 2):  # loop over the tiles in front
                    new_index = index[0] + dx, index[1] + vec[1]

                    left_tile = self.board.tile_properties((new_index[0] - 1, new_index[1]))
                    tile = self.board.tile_properties(new_index)
                    right_tile = self.board.tile_properties((new_index[0] + 1, new_index[1]))

                    if tile["blocks_movement"]:
                        offset_x = self.x - self.board.get_pos_from_index(new_index)[0]
                        if abs(offset_x) < self.width - 1:
                            # print("hit y")
                            if abs(offset_x) > self.CORNER_THRESH * self.width:
                                if offset_x < 0 and left_tile["blocks_movement"] is False:
                                    # print("left", dx)
                                    move([-1, 0])
                                elif offset_x >= 0 and right_tile["blocks_movement"] is False:
                                    # print("right", dx)
                                    move([1, 0])
                                else:
                                    move([0, -vec[1]])
                            else:
                                move([0, -vec[1]])
                            break

    def change_direction(self):
        # todo approach to both fix getting stuck and emulate original Super Bomberman movement
        #  use more checks eg surrounding tiles, and whether change is perp or parallel to previous direction
        x, y = self.board.get_pos_in_tile((self.x, self.y))
        # if abs(x) < 0.25 and abs(y) < 0.25:
        self.movement_direction = self.control_direction

    def place_bomb(self):
        if self.bombs_active < self.bomb_count:
            self.bombs.append(Bomb(self))
            self.bombs_active += 1

    def punch(self):
        self.time_punched = time.time()

    def set_pos(self, pos):
        self.x, self.y = pos

    def set_tile_pos(self, index):
        width, height = self.board.get_tile_size()
        self.set_pos((int((index[0] + 0.5) * width), int((index[1] + 0.5) * height)))

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
        self.control_direction = direction

    def set_is_moving(self, is_moving):
        self.is_moving = is_moving

    def get_direction(self):
        return self.movement_direction

    def get_is_moving(self):
        return self.is_moving

    def get_pos(self):
        return self.x, self.y

    def get_colour(self):
        return self.colour

    def get_tile_pos(self):
        return self.board.get_index_from_pos((self.x, self.y))

    def get_id(self):
        return self.player_name

    def get_size(self):
        return self.width, self.height

    def set_alive(self, is_alive):
        self.is_alive = is_alive


class Bomb:
    dud_chance = 0.05
    chain_time = 0.2  # delay between explosions in chain reactions

    def __init__(self, owner):
        self.time_created = time.time()
        self.owner = owner
        self.x, self.y = self.owner.get_pos()
        self.fuse_time = 2.5
        self.radius = self.owner.get_bomb_radius()
        self.inactive = False
        self.dud_time = 0

        self.in_flame = False
        self.flame_time = 0

        if random() < self.dud_chance:
            self.inactive = True
            self.dud_time = randint(5, 15)

    def tick(self):
        if self.fuse_time <= 0:
            return

        delta = time.time() - self.time_created

        if self.inactive and delta > self.dud_time:
            self.inactive = False
            self.time_created = time.time()

        if not self.inactive and delta > self.fuse_time:
            self.explode()

    def inside_flame(self):
        self.in_flame = True
        self.flame_time = time.time()

    def explode(self):
        self.destroy()
        tile_x, tile_y = self.owner.board.get_index_from_pos((self.x, self.y))
        self.owner.board.create_explosion((tile_x, tile_y), self.radius)

    def destroy(self):
        self.owner.remove_bomb(self)
