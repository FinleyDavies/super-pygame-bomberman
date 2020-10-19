import time
from random import random, randint, choice
from threading import Thread
from time import sleep


class Player:
    MOVEMENT_VECTORS = [
        [0, -1], [-1, -1], [-1, 0], [-1, 1],
        [0, 1], [1, 1], [1, 0], [1, -1],
    ]

    PUNCH_TIME = 500
    CORNER_THRESH = 0.5 - 0.1

    COLOURS = [(232, 232, 232), (32, 32, 232), (232, 32, 32), (32, 32, 32)]

    def __init__(self, board, player_name, player_id):
        self.player_name = player_name
        self.player_id = player_id # Number 1-4 to determine colour of player

        self.board = board
        self.board.add_player(self)
        self.width, self.height = self.board.get_tile_size_float()
        self.x, self.y = self.board.random_spawn()
        self.is_alive = True

        self.speed = self.width / 15
        self.bomb_count = 50
        self.bomb_radius = 4
        self.bombs_active = 0
        self.bombs = []
        self.powerups = [False, False, False, False]
        self.movement_direction = 2  # facing downwards
        self.control_direction = 2
        self.is_moving = False
        self.time_punched = 0
        self.colour = self.COLOURS[self.player_id % 4]

    def update(self):
        self.update_pos()
        for bomb in self.bombs:
            bomb.update()

        if self.board.tile_properties(self.get_tile_pos())["name"] == "flame":
            self.x, self.y = self.board.random_spawn()

    def update_pos(self):
        if not self.is_moving:
            return

        index = self.board.get_index_from_pos(self.get_pos())
        normal_pos = self.board.get_pos_in_tile(self.get_pos())

        def get_tiles_ahead(vec):

            def test_thread(x, y):
                self.board.set_tile((x, y), "flame")
                sleep(0.1)
                self.board.set_tile((x, y), "floor")

            x = index[0] + vec[0]
            y = index[1] + vec[1]

            t = Thread(target=test_thread, args=(x, y))
            #t.start()

            tiles = [self.board.tile_properties((x, y))["blocks_movement"]]
            if distance_to_center([vec[1], vec[0]]) == 0:
                tiles.append(True)
                return tiles
            if vec[0]:
                direction = [1, -1][normal_pos[1]<0] # switch y
                y += direction
            elif vec[1]:
                direction = [1, -1][normal_pos[0]<0]
                x += direction
            else:
                # shouldn't happen
                return tiles

            u = Thread(target=test_thread, args=(x,y))
            #u.start()
            tile = self.board.tile_properties((x, y))
            tiles.append(tile["blocks_movement"])
            return tiles

        def within_corner_cut(vec):
            if vec[0] and abs(normal_pos[1]) <= self.CORNER_THRESH:
                return True
            elif vec[1] and abs(normal_pos[0]) <= self.CORNER_THRESH:
                return True
            return False

        def cut_corner(vec):
            vector = [0, 0]
            if vec[0]:
                vector[0] = vec[0]
                vector[1] = [-1, 1][normal_pos[1]<0]
            elif vec[1]:
                vector[1] = vec[1]
                vector[0] = [-1, 1][normal_pos[0]<0]

            return vector

        def distance_to_center(vec, orth=False):
            x = -normal_pos[0] * self.width * [1, -1][vec[0]<0]
            y = -normal_pos[1] * self.height * [1, -1][vec[1]<0]
            if vec[0]:
                return x
            if vec[1]:
                return y


        def get_vectors(direction):
            vectors = list()
            if direction % 2 == 0:
                vectors.append(self.MOVEMENT_VECTORS[direction])
            else:
                # split components into separate vectors
                vectors.append(self.MOVEMENT_VECTORS[(direction - 1) % 8])
                vectors.append(self.MOVEMENT_VECTORS[(direction + 1) % 8])

            return vectors

        def get_case(vec):
            vec2 = get_vectors(self.movement_direction)[0]

            if distance_to_center(vec) <= 0:
                front, side = get_tiles_ahead(vec)
                if not (front or side):     # if nothing in front of player
                    return 1

                elif not front and side:    # if only side tile is obstructive
                    if distance_to_center([vec[1], vec[0]]) == 0:   # if the player is in the center of the tile
                        return 1
                    elif within_corner_cut(vec):    # if the player is within corner cut of the side tile
                        return 2
                    elif not (vec[0] and vec2[0]) ^ (vec[1] and vec2[1]):
                        return 3
                    else:
                        return 4

                elif front and not side:
                    if not (vec[0] and vec2[0]) ^ (vec[1] and vec2[1]): # if movement perpendicular to player direction
                        return 3                                        # only works for single component vectors
                    else:
                        return 4

                elif front and side:
                    return 4

            # elif distance_to_center(vec) < self.speed:
            #     return 5

            return 1

        def move(vec, center_stop=True, distance=1.0, change_direction=True):
            if vec[0] and vec[1]: # if moving diagonally
                move([vec[0], 0], center_stop, 0.707, change_direction)
                move([0, vec[1]], center_stop, 0.707, change_direction)
                return

            dist = self.speed * distance
            if center_stop:
                center = distance_to_center(vec)
                if 0 < center < dist:
                    dist = abs(center)

            self.x += vec[0] * dist
            self.y += vec[1] * dist

            if change_direction:
                self.movement_direction = self.MOVEMENT_VECTORS.index(vec)



        vecs = get_vectors(self.control_direction)

        if len(vecs) == 1:
            vec = vecs[0]

            case = get_case(vec)
            # print(case)
            if case == 1:
                move(vec)
            elif case == 2:
                self.movement_direction = self.MOVEMENT_VECTORS.index(vec)
                move(cut_corner(vec), change_direction=False)
            elif case == 3:
                move(self.MOVEMENT_VECTORS[self.movement_direction])
            elif case == 4:
                self.movement_direction = self.MOVEMENT_VECTORS.index(vec)

        elif len(vecs) == 2:
            cases = {get_case(vecs[0]):vecs[0], get_case(vecs[1]):vecs[1]}
            # print(*cases.keys())
            combined = [x+y for x,y in zip(*vecs)]
            if cases.keys() == {1, 1}:
                move(combined)
            if cases.keys() == {1, 2}:
                if distance_to_center(cases[1]) > 0:
                    move(cut_corner(cases[2]))
                else:
                    move(cases[1])
            if cases.keys() == {1, 3}:
                move(cases[1])
            if cases.keys() == {1, 4}:
                move(cases[1])
            if cases.keys() == {2, 2}:
                move(cut_corner(cases[2]))


    def place_bomb(self):
        if self.bombs_active < self.bomb_count and self.board.tile_properties(self.get_tile_pos())["name"] == "floor":
            self.bombs.append(Bomb(self))
            self.bombs_active += 1

    def punch(self):
        self.time_punched = time.time()

    def set_pos(self, pos):
        self.x, self.y = pos

    def get_pos(self, snap=False):
        if snap:
            index = self.get_tile_pos()
            x, y = self.board.get_pos_from_index(index)
            return int(x), int(y)
        return int(self.x), int(self.y)

    def set_tile_pos(self, index):
        width, height = self.board.get_tile_size()
        self.set_pos((int((index[0] + 0.5) * width), int((index[1] + 0.5) * height)))

    def is_punching(self):
        return (time.time() - self.time_punched * 1000) < self.PUNCH_TIME

    def remove_bomb(self, bomb):
        self.bombs.remove(bomb)
        self.bombs_active -= 1

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

    def get_bombs(self):
        return self.bombs


class Bomb:
    dud_chance = 0
    chain_time = 0.1  # delay between explosions in chain reactions

    def __init__(self, owner):
        self.time_created = time.time()
        self.owner = owner
        self.x, self.y = self.owner.get_pos(True)
        self.index = self.owner.board.get_index_from_pos((self.x, self.y))
        self.fuse_time = 2.5
        self.radius = self.owner.get_bomb_radius()
        self.inactive = False
        self.dud_time = 0

        self.in_flame = False
        self.flame_time = 0

        if random() < self.dud_chance:
            self.inactive = True
            self.dud_time = randint(5, 15)

        self.owner.board.set_tile(self.index, "bomb")

    def update(self):
        if self.fuse_time <= 0:
            return 0

        delta = time.time() - self.time_created

        in_flame = self.owner.board.tile_properties(self.index)["name"] == "flame"

        if not self.in_flame and in_flame:
            self.explode(True)
            self.in_flame = True

        if self.inactive and delta > self.dud_time:
            self.inactive = False
            self.time_created = time.time()


        if not self.inactive and delta > self.fuse_time:
            self.explode()


    def explode(self, delayed=False):
        if delayed:
            self.time_created = time.time() + self.chain_time - self.fuse_time
        else:
            self.destroy()
            tile_x, tile_y = self.owner.board.get_index_from_pos((self.x, self.y))
            self.owner.board.create_explosion((tile_x, tile_y), self.radius)

    def destroy(self):
        self.owner.remove_bomb(self)

    def get_pos(self):
        return int(self.x), int(self.y)
