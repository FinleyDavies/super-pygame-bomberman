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

            else:
                for controller in self.controllers:
                    pressed_buttons = controller.get_buttons_pressed()
                    for pressed_button in pressed_buttons:
                        if pressed_button in self.controls:
                            previously_pressed = self.keystate[self.controls[pressed_button]]
                            self.keystate[self.controls[pressed_button]] = True

                    # if there is a button in keystate that isnt in pressed_buttons then it should be not pressed
                    for valid_button in self.keystate:



                # for controller in self.controllers:
                #     buttons_pressed = controller.get_buttons_pressed()
                #
                #     for action, pressed in self.keystate.items():
                #         p = False
                #         valid_button = False
                #         for button in buttons_pressed:
                #             if button in self.controls:
                #                 valid_button = True
                #                 if action == self.controls[button]:
                #                     p = True
                #                     if not pressed:
                #                         self.keystate[action] = True
                #                         if action in ["up", "left", "down", "right"]:
                #                             updated = True
                #         if valid_button and not p:
                #             if pressed:
                #                 self.keystate[action] = False
                #                 if action in ["up", "left", "down", "right"]:
                #                     updated = True

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
        for event in pygame.event.get():
            binding.push_event(event)

        binding.update_keystate()
        print("\n"*11)
        print(binding.keystate)
        clock.tick(30)

if __name__ == "__main__":
    main()