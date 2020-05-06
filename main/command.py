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

	def __init__(self, target, position, new_tile):
		super().__init__(target)
		self.position = position
		self.new_tile = new_tile

	def execute(self):
		self.target.set_tile(self.position, self.new_tile)