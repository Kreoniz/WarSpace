import sys
import os
import pygame

from general_functions import load_image

menu_height = 50
# classes

class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, menu_height + tile_height * pos_y)

class TowerBaseTile(Tile):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tile_type, pos_x, pos_y)


# game initialization
pygame.init()
screen = pygame.display.set_mode((1100, 700))

# functions
def generate_level(level):
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '1':
                Tile('grass', x, y)
            elif level[y][x] == '2':
                Tile('road', x, y)
            elif level[y][x] == '3':
                TowerBaseTile('tower_base', x, y)
    return None

def load_level(filename):
    with open(filename, 'r') as mapFile:
        level_map = ["".join(line.split()) for line in mapFile]
    max_width = max(map(len, level_map))
    return level_map

# constants
tile_images = {'road': load_image('Textures/stone.png'),
               'grass': load_image('Textures/grass.png'),
               'tower_base': load_image('Textures/tower_base.png')
}
tile_width = tile_height = 50
all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()

cursor_select = load_image("game_assets/cursor/cursor_select.png")
cursor = load_image("game_assets/cursor/cursor.png")


# main cycle
if __name__ == '__main__':
    running = True
    pygame.mouse.set_visible(False)
    in_progress = generate_level(load_level('map.txt'))

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((0, 0, 0))
        all_sprites.draw(screen)

        if pygame.mouse.get_focused():
            if any(pygame.mouse.get_pressed()):
                screen.blit(cursor_select, pygame.mouse.get_pos())
            else:
                screen.blit(cursor, pygame.mouse.get_pos())

        pygame.display.flip()
    pygame.quit()
