import sys
import os
import pygame
import math
import random as rd
from pprint import pprint


# importing other stuff ------------------------------------------------------------------------------------------------
from general_functions import load_image, create_fonts

menu_height = 0
vacant_bases = {}
occupied_bases = {(3, 2): 1}

# classes --------------------------------------------------------------------------------------------------------------

class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, menu_height + tile_height * pos_y)


class TowerBaseTile(Tile):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tile_type, pos_x, pos_y)
        self.pos = pos_x, pos_y

    def tower_options(self):
        if self.pos in occupied_bases:
            print("yes")
        else:
            print("not")

    def update(self):
        self.tower_options()

# class Info_bar:
#     def __init__(self, screen):
#         self.image = load_image('game_assets/info_bar/info_bar.png')
#         screen.blit(self.image, (0, 0))

class Tower(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y, repeat=False):
        super().__init__(all_sprites, tower_group)
        self.frames = []
        self.flipped_frames = []
        self.repeat = repeat
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns, sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(frame_location, self.rect.size)))
        if self.repeat:
            for j in range(rows):
                for i in range(columns):
                    frame_location = (self.rect.w * i, self.rect.h * j)
                    self.flipped_frames.append(pygame.transform.flip(sheet.subsurface(pygame.Rect(frame_location, self.rect.size)), True, False))
            for i in range(len(self.flipped_frames) - 2, 0, -1):
                self.frames.append(self.flipped_frames[i])
        del self.flipped_frames

    def update(self):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]

# game initialization --------------------------------------------------------------------------------------------------
pygame.init()
screen = pygame.display.set_mode((1000, 600))
size = screen.get_size()

# functions ------------------------------------------------------------------------------------------------------------
def render(screen, font, text, color, pos):
    text_surface = font.render(text, 0, pygame.Color(color))
    screen.blit(text_surface, pos)

def get_pos(pos):
    return tile_width * pos[0], tile_height * pos[1]

def generate_level(level):
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '1':
                Tile('grass', x, y)
            elif level[y][x] == '2':
                Tile('road', x, y)
            elif level[y][x] == '3':
                vacant_bases[(x, y)] = (TowerBaseTile('tower_base', x, y))
    return None

def load_level(filename):
    with open(filename, 'r') as mapFile:
        level_map = ["".join(line.split()) for line in mapFile]
    # max_width = max(map(len, level_map))
    return level_map

# constants ------------------------------------------------------------------------------------------------------------
tile_images = {'road': load_image('game_assets/Textures/stone.png'),
               'grass': load_image('game_assets/Textures/grass.png'),
               'tower_base': load_image('game_assets/Textures/tower_base.png')
}
tile_width = tile_height = 50
all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
tower_group = pygame.sprite.Group()

cursor_select = load_image("game_assets/cursor/cursor_select.png")
cursor = load_image("game_assets/cursor/cursor.png")
font_sizes_list = [40, 30, 20, 10]
fonts = create_fonts(font_sizes_list)


# main loop ------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    running = True
    pygame.mouse.set_visible(False)
    generate_level(load_level('map.txt'))
    clock = pygame.time.Clock()
    pos = get_pos((8, 4))
    blue_turret = Tower(load_image("game_assets/Towers/blue_turret_file.png"), 1, 9, pos[0] - 7, pos[1] - 10, repeat=True)


    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((0, 0, 0))
        all_sprites.draw(screen)
        tower_group.update()


        # info_bar = Info_bar(screen)

        if pygame.mouse.get_focused():
            if any(pygame.mouse.get_pressed()):
                screen.blit(cursor_select, pygame.mouse.get_pos())
            else:
                screen.blit(cursor, pygame.mouse.get_pos())

        current_fps = str(int(clock.get_fps()))
        render(screen, fonts[0], text=current_fps, color=(255, 255, 255), pos=(0, 0))

        pygame.display.flip()
        clock.tick(20)
        # print(clock.get_fps())



    pygame.quit()
