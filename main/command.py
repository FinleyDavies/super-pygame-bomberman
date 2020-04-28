from abc import ABCMeta, abstractmethod


class Command(metaclass=ABCMeta):
	def __init__(self, target):
		self.target = target

	@abstractmethod
	def execute(self):
		pass


class Move(Command):
	def __init__(self, target, direction):
		super().__init__(target)
		self.direction = direction

	def execute(self):
		self.target.set_direction(self.direction)
		self.target.set_is_moving(True)


class Stop(Command):
	def execute(self):
		self.target.set_is_moving(False)


class PlaceBomb(Command):
	def execute(self):
		self.target.place_bomb()


class Punch(Command):
	def execute(self):
		self.target.punch()
