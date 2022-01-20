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
turrets = {}
enemies = []
pygame.mixer.init()
pygame.mixer.music.load("game_assets/music/C418 - Minecraft - Minecraft Volume Alpha.mp3")
pygame.mixer.music.queue("game_assets/music/Dreiton.opus")
pygame.mixer.music.play(-1)


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
        self.tower_selection_open = False
        self.range_shown = False

    def tower_type(self):
        if self.pos not in vacant_bases:
            return turrets[self.pos]

    def tower_options_select(self):
        if self.rect.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
            self.range_shown = True
        elif not self.rect.collidepoint((pygame.mouse.get_pos())) and pygame.mouse.get_pressed()[0]:
            self.range_shown = False

    def tower_build_select(self):
        if self.rect.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
            self.tower_selection_open = True
        elif not self.rect.collidepoint((pygame.mouse.get_pos())) and pygame.mouse.get_pressed()[0]:
            self.tower_selection_open = False

    def update(self, *args):
        if self.tower_selection_open:
            pos = get_pos(self.pos)
            coords = {(pos[0] + 60, pos[1]): 0,
                      (pos[0], pos[1] + 60): 1,
                      (pos[0] - 60, pos[1]): 2,
                      (pos[0], pos[1] - 60): 3,
                      # [pos[0] - 100, pos[1] - 100]
                      }
            for pic in tower_selection_images:
                screen.blit(tower_selection_images[pic], (list(coords.keys())[pic]))
            for point in coords:
                rect = pygame.Rect(point, (50, 50))
                if rect.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
                    turrets[self.pos] = (Tower(tower_types[coords[point]][1], tower_types[coords[point]][2],
                                               tower_types[coords[point]][3], pos[0] + tower_types[coords[point]][4],
                                               pos[1] + tower_types[coords[point]][5], tower_types.keys(),
                                               tower_types[coords[point]][7]))
                    vacant_bases.pop(self.pos)
                    self.tower_selection_open = False

        elif self.range_shown:
            radius = self.tower_type().range
            tower_range = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA, 32)
            pygame.draw.circle(tower_range, (255, 0, 0, 100), (radius, radius), radius)
            pos = get_pos(self.pos)
            screen.blit(tower_range, (pos[0] - 3 * radius / 4, pos[1] - 3 * radius / 4))

        if self.pos in vacant_bases:
            self.tower_build_select()
        elif self.pos not in vacant_bases:
            self.tower_options_select()


# class Info_bar:
#     def __init__(self, screen):
#         self.image = load_image('game_assets/info_bar/info_bar.png')
#         screen.blit(self.image, (0, 0))

class Tower(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y, type=0, repeat=False):
        super().__init__(all_sprites, tower_group)
        self.frames = []
        self.flipped_frames = []
        self.repeat = repeat
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)
        self.type = type
        self.range = 100

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
                    self.flipped_frames.append(
                        pygame.transform.flip(sheet.subsurface(pygame.Rect(frame_location, self.rect.size)), True,
                                              False))
            for i in range(len(self.flipped_frames) - 2, 0, -1):
                self.frames.append(self.flipped_frames[i])
        del self.flipped_frames

    def rotation(self):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]

    def update(self):
        if enemies:
            self.rotation()
        else:
            self.image = self.frames[8]


class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(all_sprites, enemy_group)
        self.width = 50
        self.height = 50
        # path = [(0, 3), (4, 3), (4, 8), (7, 8), (7, 3), (12, 3), (12, 8), (15, 8), (15, 3), (20, 3)]
        # self.path = []
        # for point in path:
        #     self.path.append(get_pos(point))
        self.path = [(-30, 150), (200, 150), (200, 400), (350, 400), (350, 150), (600, 150), (600, 400), (750, 400),
                     (750, 150), (10000, 150)]
        self.speeds = [(1, 0), (1, 0), (0, 1), (1, 0), (0, -1), (1, 0), (0, 1), (1, 0), (0, -1), (1, 0)]
        self.path_counter = 1
        self.speed_counter = 1
        self.cur_path = self.path[self.path_counter]

    def update(self):
        self.move()
        self.isEnemyAwayScreen()
        self.draw_health_bar()
        print(self.rect.x, self.rect.y)

    def isEnemyAwayScreen(self):
        if self.rect.x > 1000:
            print('Lose')

    def move(self):
        if self.rect.x >= self.path[self.path_counter][0] and self.rect.y >= self.path[self.path_counter][1]:
            self.path_counter += 1
            self.speed_counter += 1
            self.cur_path = self.path[self.path_counter]
        self.rect = self.rect.move(self.speeds[self.speed_counter][0], self.speeds[self.speed_counter][1])

    def draw_health_bar(self):
        pygame.draw.rect(screen, 'green', (self.rect.x - 1, self.rect.y - self.hit_bar_settings, 50, 10), 1)


class Ghost(Enemy):
    def __init__(self):
        super().__init__()
        self.image = load_image(f'game_assets/enemies/ghost.png')
        self.rect = self.image.get_rect().move(self.path[0][0], self.path[0][1])
        self.health = 1
        self.hit_bar_settings = 5
        #  self.enemy_speed = 1


class BigGhost(Enemy):
    def __init__(self):
        super().__init__()
        self.image = load_image(f'game_assets/enemies/big_ghost.png')
        self.rect = self.image.get_rect().move(self.path[0][0], self.path[0][1])
        self.health = 2
        self.hit_bar_settings = 10
        #  self.enemy_speed = 1


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


# files + other stuff --------------------------------------------------------------------------------------------------
tile_images = {'road': load_image('game_assets/Textures/stone.png'),
               'grass': load_image('game_assets/Textures/grass.png'),
               'tower_base': load_image('game_assets/Textures/tower_base.png')
               }
tower_selection_images = {0: load_image('game_assets/Towers/blue_turret_select.png'),
                          1: load_image('game_assets/items/test.png'),
                          2: load_image('game_assets/items/test.png'),
                          3: load_image('game_assets/items/test.png'),
                          # 4: load_image('game_assets/items/semitransparent_circle.png')
                          }
tower_types = {0: ["blue_turret", load_image("game_assets/Towers/blue_turret_file.png"), 1, 9, -7, -10, 0, True],
               1: ["blue_turret", load_image("game_assets/Towers/rhombus_turret_file.png"), 1, 9, 0, 0, 0, True],
               2: ["blue_turret", load_image("game_assets/Towers/blue_turret_file.png"), 1, 9, -7, -10, 0, True],
               3: ["blue_turret", load_image("game_assets/Towers/blue_turret_file.png"), 1, 9, -7, -10, 0, True]
               }

cursor_select = load_image("game_assets/cursor/cursor_select.png")
cursor = load_image("game_assets/cursor/cursor.png")

font_sizes_list = [40, 30, 20, 10]
fonts = create_fonts(font_sizes_list)

tile_width = tile_height = 50
# all sprite groups ----------------------------------------------------------------------------------------------------
all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
tower_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()

# main loop ------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    running = True
    pygame.mouse.set_visible(False)
    generate_level(load_level('map.txt'))
    clock = pygame.time.Clock()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEWHEEL:
                enemies.append(Ghost())

        screen.fill((0, 0, 0))
        all_sprites.draw(screen)
        tiles_group.update()
        enemy_group.update()
        tower_group.draw(screen)
        tower_group.update()

        # range = pygame.Surface((1000, 1000), pygame.SRCALPHA, 32)
        # pygame.draw.circle(range, (0, 0, 0, 100), (0, 0), 50)
        # screen.blit(range, (110, 110))

        # info_bar = Info_bar(screen)
        if pygame.mouse.get_focused():
            if any(pygame.mouse.get_pressed()):
                screen.blit(cursor_select, pygame.mouse.get_pos())
            else:
                screen.blit(cursor, pygame.mouse.get_pos())

        current_fps = str(int(clock.get_fps()))
        render(screen, fonts[0], text=current_fps, color=(255, 255, 255), pos=(0, 0))

        pygame.display.flip()
        clock.tick(50)
        # print(clock.get_fps())

    pygame.quit()
