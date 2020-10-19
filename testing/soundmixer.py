import pygame
import os
import time
pygame.mixer.init()
pygame.init()


path = os.path.abspath(os.path.join("..", "Sounds", "MenuSelect.wav"))
sound = pygame.mixer.Sound(path)

start = time.time()
for i in range(10):
	sound.play()
	time.sleep(1)
print(time.time() - start)


# WIDTH, HEIGHT = 640, 480
# screen = pygame.display.set_mode((WIDTH, HEIGHT))
#
# running = True
# while running:
# 	for event in pygame.event.get():
# 		if event.type == pygame.QUIT:
# 			running = False
#
# 	pygame.display.update()
# 	screen.fill((0, 0, 0))


pygame.quit()