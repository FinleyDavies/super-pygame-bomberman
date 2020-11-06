import pygame
import controller
import game_commands
from queue import Queue
from collections import OrderedDict
import os, json
import threading
from game_commands import *


# class that handles reading key and controller state and sending commands to the game accordingly
# and updating keybindings by providing a callback method for the ControlsMenu class

class KeyBinds:
    def __init__(self, bindings):
        self.bindings = bindings

        self.event_queue = Queue()  # pygame.event.Event
        self.pressed_queue = Queue()  # used when rebinding controls
        self.commands = list()

        self.controls = dict()
        self.reset_controls()  # str key : str action

        self.keystate = {name: False for name in self.controls.values()}  # str action : bool pressed

    def rebind_button(self, button):
        self.pressed_queue = Queue()

        def wait_for_press():
            key_name = self.pressed_queue.get()
            button.render_text(f"{button.text}: {key_name}")

        t = threading.Thread(target=wait_for_press)
        t.start()
        # wait_for_press()

    def update_keystate(self):
        while not self.event_queue.empty():
            event = self.get_event()

            if event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
                pressed = event.type == pygame.KEYDOWN
                name = pygame.key.name(event.key)
                if pressed:
                    self.pressed_queue.put(name)
                if name in self.controls:
                    self.keystate[self.controls[name]] = pressed
                    self.do_action(self.controls[name], pressed)

            elif event.type == controller.CONTROLLERBUTTONDOWN or event.type == controller.CONTROLLERBUTTONUP:
                pressed = event.type == controller.CONTROLLERBUTTONDOWN
                name = event.button
                if pressed:
                    self.pressed_queue.put(name)
                if name in self.controls:
                    self.keystate[self.controls[name]] = pressed
                    self.do_action(self.controls[name], pressed)

    def do_action(self, action, is_pressed):
        self.commands.append(self.bindings[action][is_pressed])

    def get_commands(self):
        commands = self.commands
        self.commands = list()
        return commands

    def get_event(self, block=True):
        return self.event_queue.get(block)

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
    from player_new import Player
    from board import Board
    game_board = Board.from_file_name("Arena1.txt")
    client_player = Player(game_board, "player_1", 0)

    actions = {
        "up": {
            True: UpdateDirection(client_player, 0, True),
            False: UpdateDirection(client_player, 0, False)
        },
        "left": {
            True: UpdateDirection(client_player, 2, True),
            False: UpdateDirection(client_player, 2, False)
        },
        "down": {
            True: UpdateDirection(client_player, 4, True),
            False: UpdateDirection(client_player, 4, False)
        },
        "right": {
            True: UpdateDirection(client_player, 6, True),
            False: UpdateDirection(client_player, 6, False)
        },
        "place bomb": {
            True: PlaceBomb(client_player),
            False: Dummy()
        },
        "punch": {
            True: Punch(client_player),
            False: Dummy()
        },
        "detonate": {
            True: Dummy(),
            False: Dummy()
        },
    }

    pygame.init()
    pygame.display.set_mode((500, 500))
    controllers = controller.init()
    binding = KeyBinds(actions)
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
        commands = binding.get_commands()
        if commands:
            print(commands)
        #print(binding.keystate)
        clock.tick(30)


if __name__ == "__main__":
    main()
