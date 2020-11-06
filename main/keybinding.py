import pygame
import controller
import game_commands
from queue import Queue
from collections import OrderedDict
import os, json


# class that handles reading key and controller state and sending commands to the game accordingly
# and updating keybindings by providing a callback method for the ControlsMenu class

class KeyBinds:
    def __init__(self, controllers=None):
        if controllers is None:
            controllers = []
        self.controllers = controllers
        self.event_queue = Queue() # pygame.event.Event

        self.pressed_queue = Queue()

        self.controls = dict()
        self.reset_controls() # str key : str action

        self.keystate = {name: False for name in self.controls.values()} # str action : bool pressed

    def rebind_button(self, button):
        while True:
            event = self.get_event()
            if event.type == pygame.KEYDOWN:
                break

        key_name = pygame.key.name(event.key)
        button.render_text(f"{button.text}: {key_name}")

    def update_keystate(self):
        updated = False

        while not self.event_queue.empty():
            event = self.get_event()

            if event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
                pressed = event.type == pygame.KEYDOWN
                name = pygame.key.name(event.key)
                self.pressed_queue.put(name)
                if name in self.controls:
                    self.keystate[self.controls[name]] = pressed
                    if self.controls[name] in ["up", "left", "down", "right"]:
                        updated = True

            elif event.type == controller.CONTROLLERBUTTONDOWN or event.type == controller.CONTROLLERBUTTONUP:
                pressed = event.type == controller.CONTROLLERBUTTONDOWN
                name = event.button
                self.pressed_queue.put(name)
                if name in self.controls:
                    self.keystate[self.controls[name]] = pressed
                    if self.controls[name] in ["up", "left", "down", "right"]:
                        updated = True

        return updated


    def get_event(self):
        return self.event_queue.get()

    def push_event(self, event):
        self.event_queue.put(event)



    def reset_controls(self):
        # reset the controls to the default settings
        self.load_controls("keyboard_default.json")

    def load_controls(self, file):
        # load controls from a json file
        with open(os.path.join(file), 'r+') as file:
            controls = json.load(file)
            flipped = {value: key for key, value in controls.items()}

        self.controls = flipped


def main():
    pygame.init()
    pygame.display.set_mode((500, 500))
    controllers = controller.init()
    binding = KeyBinds(controllers)
    binding.load_controls("controller_default.json")
    clock = pygame.time.Clock()
    print(pygame.key.get_focused())

    while True:
        for cont in controllers:
            cont.generate_events()
            cont.post_events()

        for event in pygame.event.get():
            binding.push_event(event)

        binding.update_keystate()
        print("\n"*11)
        print(binding.keystate)
        clock.tick(30)

if __name__ == "__main__":
    main()