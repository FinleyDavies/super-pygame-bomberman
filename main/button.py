import pygame
from time import time, sleep
from threading import Thread

#pygame.font.init()


class Button:
    FONT = pygame.font.get_default_font()
    HIGHLIGHT_SHIFT = 20
    COLOUR = (230, 230, 230)
    PRESS_TIME = 0.1

    def __init__(self, surface, rect, text="", callback=None, self_parameter=False, colour=None, font_name=None, font_size=20, interactive=True, draw_rect=True):
        self.parent_surface = surface
        self.callback = callback
        self.rect = rect
        self.width = self.rect.width
        self.self_parameter = self_parameter
        self.font_size = font_size
        self.interactive = interactive
        self.draw_rect = draw_rect

        if colour is None:
            colour = self.COLOUR
        self.colour = pygame.color.Color(*colour)

        hsva = list(self.colour.hsva)
        self.highlight_colour = pygame.color.Color(0, 0, 0)
        self.pressed_colour = pygame.color.Color(0, 0, 0)
        hsva[2] = max(0, min(100, hsva[2] - self.HIGHLIGHT_SHIFT))
        self.highlight_colour.hsva = tuple(hsva)
        hsva[2] = max(0, min(100, hsva[2] - self.HIGHLIGHT_SHIFT))
        self.pressed_colour.hsva = tuple(hsva)

        if font_name is None:
            font_name = self.FONT
        self.font_name = font_name

        self.font = pygame.font.Font(pygame.font.match_font(self.font_name), self.font_size)
        self.text = text

        self.rendered = None
        self.text_rect = None
        self.render_text(self.text)

        self.is_highlighted = False
        self.is_pressed = False
        self.time_pressed = 0

    def draw(self):
        if self.is_pressed:
            if self.draw_rect:
                pygame.draw.rect(self.parent_surface, self.pressed_colour, self.rect)
            self.parent_surface.blit(self.rendered, self.text_rect.move(0, 5))

        elif self.is_highlighted:
            if self.draw_rect:
                pygame.draw.rect(self.parent_surface, self.highlight_colour, self.rect)
            self.parent_surface.blit(self.rendered, self.text_rect)

        else:
            if self.draw_rect:
                pygame.draw.rect(self.parent_surface, self.colour, self.rect)
            self.parent_surface.blit(self.rendered, self.text_rect)

        if self.draw_rect:
            pygame.draw.rect(self.parent_surface, (10, 10, 10), self.rect, 2)

    def update(self, mouse_pos):
        if not self.interactive:
            return
        if self.rect.collidepoint(mouse_pos):
            self.is_highlighted = True
        else:
            self.is_highlighted = False

        if self.is_pressed and time() - self.time_pressed > self.PRESS_TIME:
            self.is_pressed = False

    def press(self, mouse_pos):
        if not self.interactive:
            return
        if self.rect.collidepoint(mouse_pos):
            print(f"pressed {self.text}")
            self.time_pressed = time()
            self.is_pressed = True
            if self.callback:
                if self.self_parameter:
                    self.callback(self)
                else:
                    self.callback()

    def change_text(self, text):
        self.render_text(text)


    def render_text(self, text):
        self.rendered = self.font.render(text, True, (10, 10, 10))
        self.text_rect = self.rendered.get_rect()
        self.text_rect.center = self.rect.center

        self.fit_text()

    def fit_text(self):
        if self.text_rect.width + 20 > self.width:
            rect = self.text_rect.copy()
            rect.height = self.rect.height
            rect.center = self.rect.center
            self.rect = rect.inflate(20, 0)

        elif self.text_rect.width < self.width:
            rect = self.text_rect.copy()
            rect.height = self.rect.height
            rect.width = self.width
            rect.center = self.rect.center
            self.rect = rect




if __name__ == "__main__":
    from itertools import cycle

    pygame.init()
    infoObject = pygame.display.Info()
    WIDTH, HEIGHT = (infoObject.current_w, infoObject.current_h)
    WIDTH = int(WIDTH / 1.2)
    HEIGHT = int(HEIGHT / 1.2)
    print(WIDTH, HEIGHT)
    screen = pygame.display.set_mode((WIDTH, HEIGHT))#, pygame.FULLSCREEN)
    # pygame.display.toggle_fullscreen()
    clock = pygame.time.Clock()
    # b = Button(screen, pygame.rect.Rect((50, 50, 100, 50)), "button", callback=lambda: print("pressed"))

    displays = [[852, 480],
                [1280, 720],
                [1365, 768],
                [1600, 900],
                [1920, 1080]]
    display_cycle = cycle(displays)


    def cycle_display():
        screen = pygame.display.set_mode(next(display_cycle))#, pygame.FULLSCREEN)


    buttons = list()
    width, height = 100, 50
    cols = WIDTH // (width + 5)
    print(cols)
    for i, font in enumerate(pygame.font.get_fonts()[:] + [pygame.font.get_default_font()]):
        button_rect = pygame.rect.Rect(((width + 5) * (i % cols), (height + 5) * (i // cols), 0, height))
        button_colour = pygame.color.Color("red")
        button_colour.hsva = ((360*(i%cols)//cols), 100, 100, 100)

        def name(font):
            print(font)

        def rem(f):
            for button in buttons:
                if button.font_name == f:
                    buttons.remove(button)

        button = Button(screen, button_rect, f"testing {i}", font_name=font, colour=(200,200,200), callback=lambda f=font: name(f))
        buttons.append(button)

    while True:
        [b.draw() for b in buttons]
        [b.update(pygame.mouse.get_pos()) for b in buttons]

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                for b in buttons:
                    print(b.font_name)
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    exit()

                if event.key == pygame.K_q:
                    cycle_display()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                [b.press(pygame.mouse.get_pos()) for b in buttons]
        pygame.display.update()
        screen.fill((100, 100, 100))
        clock.tick(60)
