import json

class GameObject:
    current_id = 0
    def __init__(self, object_id=None):
        if object_id is not None:
            self.object_id = object_id
        else:
            self.object_id = GameObject.current_id
            GameObject.current_id += 1

    def update(self):
        pass

    def get_id(self):
        return self.object_id

class GameObjectEncoder(json.JSONEncoder):
    def default(self, o):
        return o.__dict__

def GameObjectDecoder(kwargs):
    return
