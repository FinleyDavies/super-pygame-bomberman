import pygame
from button import Button
from random import random


class ButtonMenu:
    KEYBIND = pygame.K_ESCAPE
    FONT = "microsoftphagspa"
    BUTTON_HEIGHT = 50
    BUTTON_WIDTH = 200


    def __init__(self, screen, name=None, columns=1):
        self.name = "Main Menu" if name is None else name

        self.buttons = list()
        self.layout = [list() for _ in range(columns)]
        self.columns = columns

        self.screen = screen
        self.rect = screen.get_rect()
        self.surface = pygame.Surface(self.rect.size, pygame.SRCALPHA)

        self.is_open = False

        self.add_button("Resume Game", self.close)


    def add_button(self, name, function, column=0):
        center_x = ( self.rect.width / (self.columns + 1) ) * (column + 1)
        center_y = self.BUTTON_HEIGHT * ( len(self.layout[column]) + 1 )

        button_rect = pygame.rect.Rect(0, 0, self.BUTTON_WIDTH, self.BUTTON_HEIGHT)
        button_rect.center = (center_x, center_y)

        button = Button(self.surface, button_rect, name, function)

        self.buttons.append(button)
        self.layout[column].append(button)


    def add_menu(self, menu):
        pass


    def update(self, event):
        print("updating menu", random())
        if event.type == pygame.KEYDOWN:
            if event.key == self.KEYBIND:
                print("menu toggled")
                self.is_open = not self.is_open
                print(f"Menu open: {self.is_open}")

        if self.is_open:
            if event.type == pygame.MOUSEBUTTONDOWN:
                for button in self.buttons:
                    button.press(pygame.mouse.get_pos())

            for button in self.buttons:
                button.update(pygame.mouse.get_pos())


    def draw(self):
        if self.is_open:
            self.surface.fill((255, 255, 255, 128))
            for button in self.buttons:
                button.draw()

            self.screen.blit(self.surface, (0,0))


    def open(self):
        self.is_open = True


    def close(self):
        self.is_open = False