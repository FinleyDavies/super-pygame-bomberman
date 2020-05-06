import pygame
import os
import time
pygame.mixer.init()
pygame.init()


path = os.path.abspath(os.path.join("..", "Sounds", "Explosion.wav"))
sound = pygame.mixer.Sound(path)
sound.play()
time.sleep(0.2)
sound.play()


WIDTH, HEIGHT = 640, 480
screen = pygame.display.set_mode((WIDTH, HEIGHT))

running = True
while running:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False

	pygame.display.update()
	screen.fill((0, 0, 0))


pygame.quit()