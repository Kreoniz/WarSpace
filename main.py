import sys
import os
import pygame

from general_functions import load_image

# classes
class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)

# game initialization
pygame.init()
size = width, height = 500, 450
screen = pygame.display.set_mode(size)

# functions
def generate_level(level):
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '1':
                Tile('grass', x, y)
            elif level[y][x] == '2':
                Tile('road', x, y)
    return None

def load_level(filename):
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
    max_width = max(map(len, level_map))
    return level_map

# constants
tile_images = {'road': load_image('Textures/stone.png'),
               'grass': load_image('Textures/grass.png')}
tile_width = tile_height = 50
all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()

# main cycle
if __name__ == '__main__':
    running = True
    in_progress = generate_level(load_level('map.txt'))
    all_sprites.draw(screen)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        pygame.display.flip()
    pygame.quit()
