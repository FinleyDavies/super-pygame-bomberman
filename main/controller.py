from abc import ABCMeta, abstractmethod
from pygame import joystick

DIRECTIONS = ["UP", "LEFT", "DOWN", "RIGHT"]
ANALOG_THRESHOLD = 0.4


class ControllerBase(metaclass=ABCMeta):

    def __init__(self, controller: joystick.Joystick, name: str, id: int):
        self.controller = controller
        self.name = name
        self.id = id

    @abstractmethod
    def get_buttons_pressed(self):
        pass


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
            pressed.append(f"{self.name}_{DIRECTIONS[1 + status[1]]}")

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
                pressed.append(name)

        for component in self.components:
            pressed = pressed + component.get_buttons_pressed()

        return pressed

    def update_state(self):
        pressed = self.get_buttons_pressed()
        if self.pressed != pressed:
            self.pressed = pressed
            return pressed
        return None


def update(controllers: list):  # TODO update to pygame 2 as joysticks can't be added while running in pygame 1
    if len(controllers) != joystick.get_count():
        pass


def main():
    import pygame
    import json, os
    pygame.init()
    #pygame.display.set_mode((500, 500))
    clock = pygame.time.Clock()
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

    while True:
        pygame.event.get()
        for controller in controllers:
            buttons = controller.update_state()
            if buttons:
                print(buttons)
        clock.tick(60)

if __name__ == "__main__":
    main()
