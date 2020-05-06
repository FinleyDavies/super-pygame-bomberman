from abc import ABCMeta, abstractmethod
from time import time


class Command(metaclass=ABCMeta):
	id = 0

	def __init__(self, target, **kwargs):
		self.time_created = time()
		self.target = target
		self.kwargs = kwargs

	@abstractmethod
	def execute(self):
		pass

	def __repr__(self):
		return f"{self.__class__.__name__}({self.target}, {self.kwargs})"


class Move(Command):
	id = 1

	def __init__(self, target, direction):
		super().__init__(target)
		self.direction = direction

	def execute(self):
		self.target.set_direction(self.direction)
		self.target.set_is_moving(True)


class Stop(Command):
	id = 2

	def execute(self):
		self.target.set_is_moving(False)


class PlaceBomb(Command):
	id = 3

	def execute(self):
		self.target.place_bomb()


class Punch(Command):
	id = 4

	def execute(self):
		self.target.punch()


class UpdateTile(Command):
	id = 5

	def __init__(self, target, index, tile):
		super().__init__(target, index=index, tile=tile)
		self.index = index
		self.tile = tile

	def execute(self):
		self.target.set_tile(self.index, self.tile)
