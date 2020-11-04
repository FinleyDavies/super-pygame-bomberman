import pygame
from button import Button
from threading import Thread
from queue import Queue
from time import sleep


class Menu:
    KEYBIND = pygame.K_ESCAPE
    FONT = "microsoftphagspa"
    FONT_SIZE_BUTTON = 15
    FONT_SIZE_TITLE = 40
    FONT_SIZE_SUBTITLE = 20
    BUTTON_HEIGHT = 50
    BUTTON_WIDTH = 100

    def __init__(self, screen, name=None, columns=1):

        self.name = "Main Menu" if name is None else name

        self.title_font = pygame.font.Font(pygame.font.match_font(self.FONT), self.FONT_SIZE_TITLE)
        self.subtitle_font = pygame.font.Font(pygame.font.match_font(self.FONT), self.FONT_SIZE_SUBTITLE)
        self.title = self.title_font.render(self.name, True, (10, 10, 10))

        self.buttons = list()
        self.layout = [list() for _ in range(columns)]
        self.columns = columns

        self.screen = screen
        self.rect = screen.get_rect()
        self.surface = pygame.Surface(self.rect.size, pygame.SRCALPHA)

        self.is_open = False
        self.same_frame = False  # prevents button presses from registering twice when changing menus

        self.add_button("Resume Game", self.close)

        self.adjacents = []

    def get_button_center(self, column):
        # returns the center of the next button
        center_x = (self.rect.width / (self.columns + 1)) * (column + 1)
        center_y = self.BUTTON_HEIGHT + (self.BUTTON_HEIGHT + 10) * (len(self.layout[column]) + 1)

        return center_x, center_y

    def add_button(self, name, function, column=0, self_parameter=False):

        button_rect = pygame.rect.Rect(0, 0, self.BUTTON_WIDTH, self.BUTTON_HEIGHT)
        button_rect.center = self.get_button_center(column)

        button = Button(self.surface, button_rect, name, function, self_parameter, font_name=self.FONT,
                        font_size=self.FONT_SIZE_BUTTON)

        self.buttons.append(button)
        self.layout[column].append(button)

    def add_subtitle(self, name, column):
        button_rect = pygame.rect.Rect(0, 0, self.BUTTON_WIDTH, self.BUTTON_HEIGHT)
        button_rect.center = self.get_button_center(column)
        button = Button(self.surface, button_rect, name, font_name=self.FONT,
                        font_size=self.FONT_SIZE_SUBTITLE, interactive=False, draw_rect=False)
        self.buttons.append(button)
        self.layout[column].append(button)

    def add_menu(self, menu):
        def on_press():
            print(f"closing {self.name}")
            self.close()
            print(f"opening {menu.name}")
            menu.same_frame = True
            menu.open()

        if menu not in self.adjacents:
            self.adjacents.append(menu)
            self.add_button(menu.get_name(), on_press)
            menu.add_menu(self)

    def update(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == self.KEYBIND:
                if self.name == "Main Menu":
                    self.is_open = not self.is_open
                else:
                    self.is_open = False

        if self.is_open and not self.same_frame:
            if event.type == pygame.MOUSEBUTTONDOWN:
                for button in self.buttons:
                    button.press(pygame.mouse.get_pos())

            for button in self.buttons:
                button.update(pygame.mouse.get_pos())

        self.same_frame = False

    def draw(self):
        if self.is_open:
            self.surface.fill((255, 255, 255, 128))

            rect = self.title.get_rect()
            rect.center = (self.rect.width / 2, 30)
            self.surface.blit(self.title, rect)

            for button in self.buttons:
                button.draw()

            self.screen.blit(self.surface, (0, 0))

    def open(self):
        self.is_open = True

    def close(self):
        self.is_open = False

    def get_name(self):
        return self.name


class ControlsMenu(Menu):
    CONTROLS = {"UP": pygame.K_w, "LEFT": pygame.K_a, "DOWN": pygame.K_s, "RIGHT": pygame.K_d, "PUNCH": pygame.K_j,
                "DETONATE": pygame.K_k}

    def __init__(self, screen, players, controls):
        super().__init__(screen, "Controls", len(players) + 1)
        self.players = players
        self.controls = controls

        self.set_buttons()
        self.event_queue = Queue()
        self.changing = False

    def set_buttons(self):
        # [self.layout[i+1].append(None) for i in range(len(self.layout)-1)]
        for column, player in enumerate(self.players):
            self.add_subtitle(player, column + 1)

        for column in range(len(self.players)):
            for control in self.controls:
                self.add_button(control, self.change_binding, column + 1, True, )

    def update(self, event):
        super().update(event)
        if self.changing:
            self.event_queue.put(event)

    def change_binding(self, button, callback):
        # callback runs in separate thread and must return a string
        if self.changing:
            return

        self.changing = True
        button.change_text("Press key to assign")

        def print_key():
            while True:
                event = self.event_queue.get()
                if event.type == pygame.KEYDOWN:
                    break

            button.render_text(f"{button.text}: {pygame.key.name(event.key)}")
            self.changing = False

        t = Thread(target=print_key)
        t.start()
