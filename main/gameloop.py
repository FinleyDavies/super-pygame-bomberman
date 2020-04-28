import pygame
from sprite import testing_anim, players
import os
import time
pygame.init()

WIDTH, HEIGHT = (640, 480)
screen = pygame.display.set_mode((WIDTH, HEIGHT))


players.convert()
clock = pygame.time.Clock()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s:
                testing_anim.start_animation()
            elif event.key == pygame.K_w:
                players.scale()

    if pygame.key.get_pressed()[pygame.K_s]:
        screen.blit(testing_anim.get_current_frame(), (WIDTH // 2, HEIGHT // 2))

    pygame.display.update()
    screen.fill((16, 120, 48))
    clock.tick(60)

pygame.quit()
