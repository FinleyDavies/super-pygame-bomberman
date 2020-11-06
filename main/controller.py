from abc import ABCMeta, abstractmethod
from pygame import joystick, event, USEREVENT, JOYBUTTONUP, JOYBUTTONDOWN

DIRECTIONS = ["UP", "LEFT", "DOWN", "RIGHT"]
ANALOG_THRESHOLD = 0.4
CONTROLLERBUTTONDOWN = USEREVENT + 1
CONTROLLERBUTTONUP = USEREVENT + 2

controller_down = event.Event(CONTROLLERBUTTONDOWN, button="A", controller=0)
controller_up = event.Event(CONTROLLERBUTTONUP, button="A", controller=0)


# controller_down events created when a unique button is added to pressed
# controller_up created when

# controller key names must be all uppercase to avoid collisions with pygame.key.name (returns lowercase letter),
# as otherwise, both the a button on the controller and keyboard will have the same identifier


# TODO use pygame events directly to generate KEYDOWN and KEYUP (or other) events with custom ids to make input
#  handling easier


class ControllerBase(metaclass=ABCMeta):

    def __init__(self, controller: joystick.Joystick, name: str, id: int):
        self.controller = controller
        self.pressed = list()
        self.events = list()
        self.name = name
        self.id = id

    def get_id(self):
        return self.id

    @abstractmethod
    def get_buttons_pressed(self):
        pass

    def generate_events(self):
        prev = set(self.pressed)
        curr = set(self.get_buttons_pressed())
        if prev != curr:
            for button_down in curr.difference(prev):
                self.events.append(
                    event.Event(CONTROLLERBUTTONDOWN, button=button_down, controller=self.controller.get_id()))

            for button_up in prev.difference(curr):
                self.events.append(
                    event.Event(CONTROLLERBUTTONUP, button=button_up, controller=self.controller.get_id()))

            self.pressed = list(curr)

    def collect_events(self):
        events = self.events
        self.events = list()
        return events

    def post_events(self):
        for e in self.collect_events():
            event.post(e)


class Hat(ControllerBase):

    def __init__(self, controller: joystick.Joystick, name: str = None, id: int = 0):
        if name is None:
            name = f"HAT_{id}"

        super().__init__(controller, name, id)

    def get_buttons_pressed(self):
        pressed = list()
        status = self.controller.get_hat(0)

        if status[0] != 0:
            pressed.append(f"{self.name}_{DIRECTIONS[2 + status[0]]}")
        if status[1] != 0:
            pressed.append(f"{self.name}_{DIRECTIONS[1 - status[1]]}")

        return pressed

class AnalogStick(ControllerBase):
    def __init__(self, controller: joystick.Joystick, x_axis, y_axis, name: str = None, id: int = 0):
        if name is None:
            name = f"STICK_{id}"

        super().__init__(controller, name, id)

        self.x_axis = x_axis
        self.y_axis = y_axis

    def get_x(self):
        return self.controller.get_axis(self.x_axis)

    def get_y(self):
        return self.controller.get_axis(self.y_axis)

    def get_buttons_pressed(self):
        pressed = list()
        x, y = self.get_x(), self.get_y()

        if x < -ANALOG_THRESHOLD or x > ANALOG_THRESHOLD:
            direction = -1 if x < 0 else 1
            pressed.append(f"{self.name}_{DIRECTIONS[2 + direction]}")

        if y < -ANALOG_THRESHOLD or y > ANALOG_THRESHOLD:
            direction = -1 if y < 0 else 1
            pressed.append(f"{self.name}_{DIRECTIONS[1 + direction]}")

        return pressed


class AnalogTrigger(ControllerBase):
    def __init__(self, controller: joystick.Joystick, axis, name: str = None, id: int = 0):
        if name is None:
            name = f"TRIGGER_{id}"  # not used
        super().__init__(controller, name, id)
        self.axis = axis

    def get_value(self):
        return self.controller.get_axis(self.axis)

    def get_buttons_pressed(self):
        pressed = list()
        if self.get_value() < -ANALOG_THRESHOLD:
            pressed.append("LEFT_TRIGGER")
        if self.get_value() > ANALOG_THRESHOLD:
            pressed.append("RIGHT_TRIGGER")

        return pressed


class Controller(ControllerBase):
    def __init__(self, controller: joystick.Joystick, id: int = 0):
        super().__init__(controller, controller.get_name(), id)

        self.buttons = dict()
        self.components = list()
        self.is_loaded = False  # whether or not the controls have been loaded from a json file

        self.pressed = []

    def load_controls(self, controls: dict = None):
        if controls is None:  # only hats and buttons can be reliably mapped
            for i in range(self.controller.get_numbuttons()):
                self.buttons[i] = f"BUTTON_{i}"

            for i in range(self.controller.get_numhats()):
                self.components.append(Hat(self.controller, id=i))


        else:
            self.buttons = {index: name for name, index in controls["buttons"].items()}
            print(self.buttons)

            for i in range(self.controller.get_numhats()):
                self.components.append(Hat(self.controller, "DPAD", i))

            for i, stick_name in enumerate(controls["sticks"]):
                x_axis = controls["sticks"][stick_name]["x_axis"]
                y_axis = controls["sticks"][stick_name]["y_axis"]
                print(x_axis, y_axis)
                self.components.append(AnalogStick(self.controller, x_axis, y_axis, stick_name, i))

            for i, trigger_name in enumerate(controls["triggers"]):
                axis = controls["triggers"][trigger_name]
                print(axis)
                self.components.append(AnalogTrigger(self.controller, axis, trigger_name, i))

            self.is_loaded = True

    def get_buttons_pressed(self):
        pressed = list()
        for index, name in self.buttons.items():
            if self.controller.get_button(index):
                pressed.append(f"{name}({self.id})")

        for component in self.components:
            pressed = pressed + [f"{name}({self.id})" for name in component.get_buttons_pressed()]

        return pressed


def update(controllers: list):  # TODO update to pygame 2 as joysticks can't be added while running in pygame 1
    if len(controllers) != joystick.get_count():
        pass


def init():
    import json, os

    joystick.init()
    controllers = list()
    for i in range(joystick.get_count()):
        print("added")
        joy = joystick.Joystick(i)
        joy.init()

        controller = Controller(joy, i)

        with open(os.path.join("xbox_keys.json"), 'r+') as file:
            keys = json.load(file)
            print(keys)

        controller.load_controls(keys)
        controllers.append(controller)

    return controllers


def main():
    import pygame
    import json, os
    pygame.init()
    # pygame.display.set_mode((500, 500))
    clock = pygame.time.Clock()
    controllers = init()

    while True:
        for e in pygame.event.get():
            if e.type == CONTROLLERBUTTONDOWN:
                print("DOWN", e.button)
            elif e.type == CONTROLLERBUTTONUP:
                print("UP", e.button)

        for controller in controllers:
            controller.generate_events()
            controller.post_events()
        clock.tick(60)


if __name__ == "__main__":
    main()
