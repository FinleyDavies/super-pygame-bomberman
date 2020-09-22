from abc import ABCMeta, abstractmethod
from json import dumps

class GameObject(metaclass=ABCMeta):
    current_id = 0

    def __init__(self, id=None):
        if id is None:
            self.id = self.current_id
            GameObject.current_id += 1
        else:
            self.id = id

    @abstractmethod
    def update(self):
        pass

    def get_id(self):
        return self.id

    def serialize(self):
        serialized = dict()
        serialized["type"] = self.__class__.__name__


