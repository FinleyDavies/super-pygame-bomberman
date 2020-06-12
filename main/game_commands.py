from abc import ABCMeta, abstractmethod
from time import time
from inspect import getmembers, getmodule, isclass
from sys import modules
import json


class Command(metaclass=ABCMeta):
    def __init__(self, target, **kwargs):
        self.time_created = time()
        self.target = target
        self.kwargs = kwargs

    @abstractmethod
    def execute(self):
        pass

    def serialize(self):
        serialized = dict()
        serialized["command_name"] = self.__class__.__name__
        serialized["target"] = self.target.get_id()
        serialized["args"] = self.kwargs
        serialized = json.dumps(serialized)
        return serialized

    def __repr__(self):
        return f"{self.__class__.__name__}({self.target}, {self.kwargs})"


class Dummy(Command):
    def execute(self):
        pass


class Move(Command):
    def __init__(self, target, direction):
        super().__init__(target, direction=direction)
        self.direction = direction

    def execute(self):
        self.target.set_direction(self.direction)
        self.target.set_is_moving(True)


class SetPosition(Command):
    def __init__(self, target, x_pos, y_pos):
        super().__init__(target, x_pos=x_pos, y_pos=y_pos)
        self.x_pos = x_pos
        self.y_pos = y_pos

    def execute(self):
        self.target.set_tile_pos((self.x_pos, self.y_pos))


class Stop(Command):
    def execute(self):
        self.target.set_is_moving(False)


class PlaceBomb(Command):
    def execute(self):
        self.target.place_bomb()


class Punch(Command):
    def execute(self):
        self.target.punch()


class UpdateTile(Command):
    def __init__(self, target, index, tile):
        super().__init__(target, index=index, tile=tile)
        self.index = index
        self.tile = tile

    def execute(self):
        self.target.set_tile(self.index, self.tile)


commands_dict = {}
for name, cls in getmembers(modules[__name__], isclass):
    if getmodule(cls) == modules[__name__]:
        commands_dict[name] = cls


def deserialize(serialized, game_objects):
    serialized = json.loads(serialized)
    try:
        target = game_objects[serialized["target"]]
    except KeyError:
        return Dummy(None)

    return commands_dict[serialized["command_name"]](target, **serialized["args"])
