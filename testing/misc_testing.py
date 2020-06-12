import json
import sys
import inspect
from main.game_commands import Move

m = Move(1, 2)
print("m", m.__class__(1, 2).__class__(1, 3))
print("Move", Move)


def serialize(object):
    print(object.__class__.__name__, object.x)


class Thing:
    def __init__(self, x):
        self.x = x


class Thing2:
    def __init__(self, x, y):
        self.x = x * 2
        self.y = y


class Thing3:
    def __init__(self, x, y):
        self.x = x * 2
        self.y = y


classes = {}
for name, cls in inspect.getmembers(sys.modules[__name__], inspect.isclass):
    classes[name] = cls

print(classes)

t = Thing2(1, 3)
print("Thing2", Thing2)
serialize(t)

m = Move(t, 1)
