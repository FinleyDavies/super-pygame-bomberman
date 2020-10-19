from time import time
import json
#TODO use flyweight pattern to avoid using duplicate tiles


class Tile:
    tile_properties = json.load(open("tiles.json", "r"))
    supported_symbols = [value["symbol"] for value in tile_properties.values()]

    def __init__(self):
        self.name = "floor"
        self.symbol = "."
        self.is_solid = False
        self.destructible = True
        self.blocks_movement = False
        self.duration = 0
        self.on_explode = "flame"

        self.birth = time()
        self.age = 0

    @classmethod
    def new_tile(cls, tile_name):
        tile = cls()
        tile.set_tile(tile_name)
        return tile

    def set_properties(self, dict):
        self.__dict__.update(**dict)
        self.birth = time()
        self.age = 0

    def set_tile(self, tile_name):
        self.set_properties(self.tile_properties[tile_name])

    def update(self):
        self.age = time() - self.birth
        self.age *= 1000
        if self. duration != 0 and self.age > self.duration:
            self.kill()

    def explode(self):
        solid = self.is_solid
        if self.destructible:
            self.set_tile(self.on_explode)
        if solid:
            return True
        return False


    def kill(self):
        self.set_tile("floor")

    def __getitem__(self, item):
        return self.__dict__[item]
