import sys
import os
import pygame
from math import radians, degrees, sin, cos, tan, atan2
import random as rd
import sqlite3
import datetime as dt
# importing other stuff ------------------------------------------------------------------------------------------------
from general_functions import load_image, create_fonts, distance_between_two_points, angle_between_two_points

menu_height = 0
global_running = True
vacant_bases = {}
turrets = {}
enemies = []
wave_counter = 1
waves = 0
delay = 10
lifes = 5
counter = 3
pygame.mixer.init()
pygame.mixer.music.load("game_assets/music/C418 - Ki (Minecraft Volume Beta).mp3")
pygame.mixer.music.queue("game_assets/music/Door.mp3")
pygame.mixer.music.play(-1)

FPS = 60
money = 100

# connecting to the database -------------------------------------------------------------------------------------------
con = sqlite3.connect("score_list.db")
cur = con.cursor()


# classes --------------------------------------------------------------------------------------------------------------

class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, menu_height + tile_height * pos_y)
        self.range_shown = False


class TowerBaseTile(Tile):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tile_type, pos_x, pos_y)
        self.pos = pos_x, pos_y
        self.tower_selection_open = False
        self.range_shown = False
        global money

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
        global money
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
                characteristics = tower_types[coords[point]]
                if rect.collidepoint(pygame.mouse.get_pos()):
                    characteristics = tower_types[coords[point]]
                    render_info(f"The cost of this tower is -{characteristics[-1]}")
                    if pygame.mouse.get_pressed()[0]:
                        if money >= characteristics[-1]:
                            turrets[self.pos] = (Tower(tower_types[coords[point]][1], tower_types[coords[point]][2],
                                                       tower_types[coords[point]][3],
                                                       pos[0] + tower_types[coords[point]][4],
                                                       pos[1] + tower_types[coords[point]][5],
                                                       tower_types[coords[point]][6],
                                                       tower_types[coords[point]][7], tower_types[coords[point]][8],
                                                       tower_types[coords[point]][9],
                                                       tower_types[coords[point]][10], tower_types[coords[point]][11]))
                            money -= characteristics[-1]
                            vacant_bases.pop(self.pos)
                            self.tower_selection_open = False

        elif self.range_shown:
            radius = self.tower_type().range
            pos = get_pos(self.pos)
            tower_range = pygame.Surface(screen.get_size(), pygame.SRCALPHA, 32)
            pygame.draw.circle(tower_range, (255, 0, 0, 75), (pos[0] + tile_height / 2, pos[1] + tile_height / 2),
                               radius)
            screen.blit(tower_range, (0, 0))
            pos = get_pos(self.pos)
            coords = {(pos[0] + 60, pos[1]): 0,
                      (pos[0], pos[1] + 60): 1,
                      (pos[0] - 60, pos[1]): 2,
                      (pos[0], pos[1] - 60): 3,
                      # [pos[0] - 100, pos[1] - 100]
                      }

            for pic in tower_option_images:
                screen.blit(tower_option_images[pic], (list(coords.keys())[pic]))
            for point in coords:
                rect = pygame.Rect(point, (50, 50))
                if rect.collidepoint(pygame.mouse.get_pos()):
                    item = list(coords.keys()).index(point)
                    if item == 0:
                        refund = str(round(self.tower_type().cost * 0.6))
                        render_info(f"Selling cost: +{refund}")
                        if pygame.mouse.get_pressed()[0]:
                            money += int(refund)
                            turrets[self.pos].kill()
                            turrets.pop(self.pos)
                            vacant_bases[self.pos] = self
                            self.tower_selection_open = False
                            self.range_shown = False
                    elif item == 1:
                        pass
                    elif item == 2:
                        pass
                    elif item == 3:
                        pass

        if self.pos in vacant_bases:
            self.tower_build_select()
        elif self.pos not in vacant_bases:
            self.tower_options_select()


class Info_bar:
    def __init__(self, screen):
        self.image = load_image('game_assets/info_bar/info_bar.png')
        screen.blit(self.image, (3, 5))


class Tower(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y, type=0, repeat=False, range=100, damage=0.1, color=(255, 0, 0),
                 cost=100):
        super().__init__(all_sprites, tower_group)
        self.frames = []
        self.flipped_frames = []
        self.repeat = repeat
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)
        self.type = type
        self.range = range
        self.damage = damage
        self.color = color
        self.cost = cost

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

    def draw_line(self, enemy):
        if enemy:
            pygame.draw.circle(screen, (255, 0, 0),
                               (enemy.rect.x + enemy.rect.width / 2, enemy.rect.y + enemy.rect.height / 2), 5)
            pygame.draw.circle(screen, (255, 0, 0),
                               (self.rect.x + self.rect.width / 2, self.rect.y + self.rect.height / 2),
                               5)
            pygame.draw.line(screen, (255, 0, 0),
                             (enemy.rect.x + enemy.rect.width / 2, enemy.rect.y + enemy.rect.height / 2),
                             (self.rect.x + self.rect.width / 2, self.rect.y + self.rect.height / 2), 2)

    def hit(self, enemy):
        if enemy:
            angle = self.rotation(enemy)
            source = (self.rect.x + self.rect.width / 2 + (self.rect.width / 2 - 4) * cos(angle[0]),
                      self.rect.y + self.rect.height / 2 + (self.rect.height / 2 - 4) * sin(-angle[0]))
            target = (enemy.rect.x + enemy.rect.width / 2, enemy.rect.y + enemy.rect.height / 2)
            pygame.draw.line(screen, self.color, source, target, 4)
            if self.type == 1:
                create_particles(target)

    def enemy_detection(self):
        for num, enemy in enumerate(enemies):
            points = (enemy.rect[0], enemy.rect[1]), (enemy.rect[0] + enemy.rect[2], enemy.rect[1]), (
                enemy.rect[0] + enemy.rect[2], enemy.rect[1] + enemy.rect[3]), (
                         enemy.rect[0], enemy.rect[1] + enemy.rect[3])
            for point in points:
                if distance_between_two_points(point, (
                        self.rect.x + tile_width / 2, self.rect.y + tile_height / 2)) <= self.range:
                    enemy.hit(self.damage)
                    enemy.enemy_num = num
                    return enemy
        return False

    def rotation(self, enemy):
        angle = 22.5
        angle_between_enemy_and_tower = angle_between_two_points(
            (self.rect.x + self.rect.width / 2, self.rect.y + self.rect.height / 2),
            (enemy.rect.x + enemy.rect.width / 2, enemy.rect.y + enemy.rect.height / 2))

        if angle_between_enemy_and_tower[1] < 90:
            self.cur_frame = int(abs((angle_between_enemy_and_tower[1] - 90) // angle))
        else:
            self.cur_frame = -int(abs((angle_between_enemy_and_tower[1] - 90) // angle))
        self.image = self.frames[self.cur_frame]
        return angle_between_enemy_and_tower

    def update(self):
        if self.enemy_detection():
            self.rotation(self.enemy_detection())
            self.hit(self.enemy_detection())
            for tile in tiles_group:
                if tile.range_shown and self.rect.collidepoint((tile.rect.x, tile.rect.y)):
                    self.draw_line(self.enemy_detection())


class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(all_sprites, enemy_group)
        self.width = 50
        self.height = 50
        self.health = 50
        self.path = path
        self.enemy_num = 0
        self.speeds = [1, 0]
        self.path_counter = 0
        self.speed_counter = 1
        self.hit_bar_settings = 5
        self.cur_path = self.path[self.path_counter]
        self.hit_bar_const = 50

    def update(self):
        self.move()
        self.isEnemyAwayScreen()
        self.draw_health_bar()
        self.check_hp()
        ## print(self.rect.x, self.rect.y)

    def isEnemyAwayScreen(self):
        if self.rect.x >= 1000:
            global lifes
            lifes -= 1
            self.kill_self()
            return True

    def move(self):
        if self.rect.x < size[0]:
            if self.rect.x == self.cur_path[0] and self.rect.y == self.cur_path[1]:
                self.findingCorrectSpeed()
                self.path_counter += 1
                self.cur_path = self.path[self.path_counter]
            self.rect = self.rect.move(self.speeds[0], self.speeds[1])

    def findingCorrectSpeed(self):
        # x
        if self.cur_path[0] < self.path[self.path_counter + 1][0]:
            self.speeds[0] = 1
            self.image = load_image(self.images[0])
        elif self.cur_path[0] == self.path[self.path_counter + 1][0]:
            self.speeds[0] = 0
        # y
        if self.cur_path[1] > self.path[self.path_counter + 1][1]:
            self.speeds[1] = -1
            self.image = load_image(self.images[2])
        elif self.cur_path[1] < self.path[self.path_counter + 1][1]:  #
            self.speeds[1] = 1
            self.image = load_image(self.images[1])
        elif self.cur_path[1] == self.path[self.path_counter + 1][1]:  #
            self.speeds[1] = 0

    def draw_health_bar(self):
        pygame.draw.rect(screen, 'black', (self.rect.x - 1, self.rect.y - self.hit_bar_settings, 50, 10), 1)
        if self.health > 38:
            pygame.draw.rect(screen, 'green', (self.rect.x - 1, self.rect.y - self.hit_bar_settings, self.health, 10),
                             0)
        elif self.health > 20:
            pygame.draw.rect(screen, 'orange', (self.rect.x - 1, self.rect.y - self.hit_bar_settings, self.health, 10),
                             0)
        else:
            pygame.draw.rect(screen, 'red', (self.rect.x - 1, self.rect.y - self.hit_bar_settings, self.health, 10), 0)

    def hit(self, damage):
        self.health -= (damage * self.health_coeff)

    def check_hp(self):
        if self.health <= 0:
            self.kill_self()

    def kill_self(self):
        if self.isEnemyAwayScreen:
            global money
            money += self.cost
        enemies.pop(self.enemy_num)
        self.kill()


class Ghost(Enemy):
    def __init__(self):
        super().__init__()
        self.images = ['game_assets/enemies/ghost_right.png',
                       'game_assets/enemies/ghost_down.png',
                       'game_assets/enemies/ghost_up.png']
        self.image = load_image(self.images[0])
        self.rect = self.image.get_rect().move(self.path[0][0], self.path[0][1])
        self.health_coeff = 1
        self.cost = 25


class InvertedGhost(Enemy):
    def __init__(self):
        super().__init__()
        self.images = ['game_assets/enemies/inverted_ghost_right.png',
                       'game_assets/enemies/inverted_ghost_down.png',
                       'game_assets/enemies/inverted_ghost_up.png']
        self.image = load_image(self.images[0])
        self.rect = self.image.get_rect().move(self.path[0][0], self.path[0][1])
        self.health_coeff = 0.6
        self.cost = 50
        #  self.enemy_speed = 1


class Start_screen(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(all_sprites, start_screen_group)
        self.image = load_image('game_assets/start_screen/play_btn.png')
        self.rect = self.image.get_rect().move(442, 200)

    def update(self):
        global end_start_screen
        if self.rect.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
            self.kill()
            end_start_screen = True
        else:
            end_start_screen = False


class MapChoice(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(map_choice_group)
        self.cur_coords = [100, 200]
        self.images = ['game_assets/map_choice/easy_icon.png',
                       'game_assets/map_choice/medium_icon.png',
                       'game_assets/map_choice/hard_icon.png']

    def update(self):
        self.draw()
        self.collide()

    def draw(self):
        for img in self.images:
            screen.blit(load_image(img), self.cur_coords)
            self.cur_coords[0] += 300
        self.cur_coords = [100, 200]

    def collide(self):
        global end_map_choice_screen
        global level
        global counter
        if counter != 0:
            counter -= 1
        for img in self.images:
            image = load_image(img)
            rect = image.get_rect().move(self.cur_coords)
            if rect.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0] and counter == 0:
                if 'easy' in img:
                    level = 'map1.txt'
                if 'medium' in img:
                    level = 'map2.txt'
                if 'hard' in img:
                    level = 'map3.txt'
                end_map_choice_screen = True
                return
            self.cur_coords[0] += 300
        self.cur_coords = [100, 200]


# game initialization --------------------------------------------------------------------------------------------------
pygame.init()
screen = pygame.display.set_mode((1000, 600))
size = screen.get_size()
pygame.display.set_caption("WarSpace")
img = pygame.image.load("game_assets/zergling.png")
pygame.display.set_icon(img)
from Particles import *


# milliseconds_play = 1000
# timer_event = pygame.USEREVENT + 1
# pygame.time.set_timer(timer_event, milliseconds_play)


# functions ------------------------------------------------------------------------------------------------------------
def render(screen, font, text, color, pos):
    text_surface = font.render(text, 0, pygame.Color(color))
    screen.blit(text_surface, pos)


def get_pos(pos):
    return tile_width * pos[0], tile_height * pos[1]


def get_scores():
    result = cur.execute("""SELECT * FROM scores""").fetchall()
    return result


def generate_level(level):
    counter = 0
    for y in range(len(level)):
        row = []
        for x in range(len(level[y])):
            if level[y][x] == '1':
                Tile('grass', x, y)
                row.append(1)
            elif level[y][x] == '2':
                Tile('road', x, y)
                row.append(2)
                counter += 1
            elif level[y][x] == '3':
                vacant_bases[(x, y)] = (TowerBaseTile('tower_base', x, y))
                row.append(3)
            elif level[y][x] == '4':
                Tile('tree', x, y)
                row.append(4)
        map.append(row)
    return counter


def generate_path(road_tiles_count):
    # finding first road tile
    path = []
    for num, row in enumerate(map):
        if row[0] == 2:
            last_cord = [num, 0]
            path.append((0, num * tile_size))
    temp_cords = []
    for i in range(road_tiles_count - 1):
        if map[last_cord[0] + 1][last_cord[1]] == 2 and [last_cord[0] + 1, last_cord[1]] not in temp_cords:
            last_cord = [last_cord[0] + 1, last_cord[1]]
            path.append((last_cord[1] * tile_size, (last_cord[0] + 1) * tile_size - 50))
            temp_cords.append(last_cord)
        elif map[last_cord[0] - 1][last_cord[1]] == 2 and [last_cord[0] - 1, last_cord[1]] not in temp_cords:
            last_cord = [last_cord[0] - 1, last_cord[1]]
            path.append((last_cord[1] * tile_size, (last_cord[0] - 1) * tile_size + 50))
            temp_cords.append(last_cord)
        elif map[last_cord[0]][last_cord[1] + 1] == 2 and [last_cord[0], last_cord[1] + 1] not in temp_cords:
            last_cord = [last_cord[0], last_cord[1] + 1]
            path.append(((last_cord[1] + 1) * tile_size - 50, last_cord[0] * tile_size))
            temp_cords.append(last_cord)
        elif map[last_cord[0]][last_cord[1] - 1] == 2 and [last_cord[0], last_cord[1] - 1] not in temp_cords:
            last_cord = [last_cord[0], last_cord[1] - 1]
            path.append(((last_cord[1] - 1) * tile_size, last_cord[0] * tile_size))
            temp_cords.append(last_cord)
    path.append(((last_cord[1] + 1) * tile_size, last_cord[0] * tile_size))
    path.append(((last_cord[1] + 1) * tile_size, last_cord[0] * tile_size))
    return list(dict.fromkeys(path))


def load_level(filename):
    with open(filename, 'r') as mapFile:
        level_map = ["".join(line.split()) for line in mapFile]
    # max_width = max(map(len, level_map))
    return level_map


def enemySpawn():
    global delay
    global waves
    global wave_counter
    if wave_counter < len(level_waves):
        if waves >= level_waves[wave_counter]:
            wave_counter += 1
            waves = 0
            delay = 10
        if wave_counter == 1:
            renderWave(wave_counter)
            if delay % 1000 == 0:
                a = rd.randint(1, 5)
                if 1 <= a <= 3:
                    enemies.append(Ghost())
                else:
                    enemies.append(InvertedGhost())
                delay += 10
                waves += 1
            else:
                delay += 10
        elif wave_counter == 2:
            renderWave(wave_counter)
            if delay % 1000 == 0:
                a = rd.randint(1, 6)
                if 1 <= a <= 3:
                    enemies.append(Ghost())
                else:
                    enemies.append(InvertedGhost())
                delay += 10
                waves += 1
            else:
                delay += 10
        elif wave_counter == 3:
            renderWave(wave_counter)
            if delay % 1000 == 0:
                a = rd.randint(1, 5)
                if 1 <= a <= 3:
                    enemies.append(Ghost())
                else:
                    enemies.append(InvertedGhost())
                delay += 10
                waves += 1
            else:
                delay += 10
    else:
        renderWave(wave_counter)


def checkGameStatus():
    if lifes == 0 or (wave_counter >= len(level_waves) and len(enemies) == 0):
        return False
    else:
        return True


def renderInfoBar():
    info_bar = Info_bar(screen)
    render(screen, fonts[1], text=str(lifes), color=(255, 255, 255), pos=(50, 54))


def fpsRender(current_fps):
    render(screen, fonts[1], text=current_fps, color=(255, 255, 255), pos=(970, 565))


def render_money():
    render(screen, fonts[1], text=str(money), color=(255, 255, 255), pos=(125, 54))


def renderWave(wave):
    render(screen, fonts[1], text=(str(wave) + '/' + str(len(level_waves))), color=(255, 255, 255), pos=(120, 8))


def render_info(message):
    info = pygame.Surface(screen.get_size(), pygame.SRCALPHA, 32)
    pygame.draw.polygon(info, (100, 100, 100, 150), (
        (int(width / 2 - len(message) * 10 / 2 - 10), height - 50),
        (int(width / 2 + len(message) * 10 / 2 + 20), height - 50),
        (int(width / 2 + len(message) * 10 / 2 + 20), height - 15),
        (int(width / 2 - len(message) * 10 / 2 - 10), height - 15)))
    screen.blit(info, (0, 0))
    render(screen, fonts[1], text=message, color=(255, 255, 255),
           pos=(int(width / 2 - len(message) * 10 / 2), height - 50))


# files + other stuff --------------------------------------------------------------------------------------------------
tile_images = {'road': load_image('game_assets/Textures/stone.png'),
               'grass': load_image('game_assets/Textures/grass.png'),
               'tower_base': load_image('game_assets/Textures/tower_base.png')
               }
tower_selection_images = {0: load_image('game_assets/Towers/blue_turret_select.png'),
                          1: load_image('game_assets/Towers/red_turret_select.png'),
                          2: load_image('game_assets/Towers/negative_turret_select.png'),
                          3: load_image('game_assets/Towers/angel_turret_select.png'),
                          }
tower_option_images = {0: load_image("game_assets/tower_options/sell_tower.png"), }
tower_types = {
    0: ["blue_turret", load_image("game_assets/Towers/blue_turret_file.png"), 1, 9, -7, -10, 0, True, 125, 0.04,
        (0, 128, 255), 50],
    1: ["red_turret", load_image("game_assets/Towers/red_turret_file.png"), 1, 9, -7, -10, 1, True, 75, 0.1,
        (255, 165, 0), 100],
    2: ["negative_turret", load_image("game_assets/Towers/negative_turret_file.png"), 1, 9, -7, -10, 2, True, 200, 0.05,
        (204, 204, 100), 100],
    3: ["angel_turret", load_image("game_assets/Towers/angel_turret_file.png"), 1, 9, -7, -10, 3, True, 325, 0.05,
        (192, 192, 192), 250]
}

# ghosts # inverted ghosts # super ghosts
level_waves = [10, 20, 30]
level = 'map2.txt'

cursor_select = load_image("game_assets/cursor/cursor_select.png")
cursor = load_image("game_assets/cursor/cursor.png")

font_sizes_list = [40, 30, 20, 10]
fonts = create_fonts(font_sizes_list)

map = []

tile_size = tile_width = tile_height = 50
# all sprite groups ----------------------------------------------------------------------------------------------------
all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
tower_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
map_choice_group = pygame.sprite.Group()
start_screen_group = pygame.sprite.Group()

# main loop ------------------------------------------------------------------------------------------------------------
while global_running:
    if __name__ == '__main__':
        # default game settings
        vacant_bases = {}
        turrets = {}
        enemies = []
        wave_counter = 1
        waves = 0
        lifes = 5
        counter = 4
        all_sprites = pygame.sprite.Group()
        tiles_group = pygame.sprite.Group()
        tower_group = pygame.sprite.Group()
        enemy_group = pygame.sprite.Group()
        map_choice_group = pygame.sprite.Group()
        start_screen_group = pygame.sprite.Group()
        map = []
        money = 100
        # default game settings
        running = True
        quit_flag = False
        pygame.mouse.set_visible(False)
        clock = pygame.time.Clock()
        end_start_screen = False
        end_map_choice_screen = False
        end_screen = False
        Start_screen()
        while (end_start_screen == False):
            screen.fill((0, 0, 0))
            screen.blit(load_image('game_assets/start_screen/background.png'), (0, 0))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    end_start_screen = True
                    global_running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    start_screen_group.update()
                    if end_start_screen == True:
                        MapChoice()
                        while (end_map_choice_screen == False):
                            screen.fill((0, 0, 0))
                            screen.blit(load_image('game_assets/map_choice/background.png'), (0, 0))
                            for event in pygame.event.get():
                                if event.type == pygame.QUIT:
                                    running = False
                                    end_start_screen = True
                                    end_map_choice_screen = True
                                    global_running = False
                                if event.type == pygame.MOUSEBUTTONDOWN:
                                    pass
                            map_choice_group.update()
                            if pygame.mouse.get_focused():
                                if any(pygame.mouse.get_pressed()):
                                    screen.blit(cursor_select, pygame.mouse.get_pos())
                                else:
                                    screen.blit(cursor, pygame.mouse.get_pos())
                            pygame.display.flip()
            start_screen_group.draw(screen)
            if pygame.mouse.get_focused():
                if any(pygame.mouse.get_pressed()):
                    screen.blit(cursor_select, pygame.mouse.get_pos())
                else:
                    screen.blit(cursor, pygame.mouse.get_pos())
            pygame.display.flip()

        path = generate_path(generate_level(load_level('maps/{}'.format(level))))

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    quit_flag = True
                    global_running = False

            # screen update
            screen.fill((0, 0, 0))

            # interaction with tiles
            all_sprites.draw(screen)
            tiles_group.update()
            enemy_group.update()
            tower_group.draw(screen)
            tower_group.update()
            particle_group.draw(screen)
            particle_group.update()

            # mouse replacement
            if pygame.mouse.get_focused():
                if any(pygame.mouse.get_pressed()):
                    screen.blit(cursor_select, pygame.mouse.get_pos())
                else:
                    screen.blit(cursor, pygame.mouse.get_pos())

            # interfase render
            fpsRender(str(int(clock.get_fps())))
            renderInfoBar()
            render_money()
            enemySpawn()

            # check game status
            if not quit_flag:
                running = checkGameStatus()

            # others
            pygame.display.flip()
            clock.tick(FPS)

            if not checkGameStatus():
                end_screen = True

        # end_screen -----------------------------------------------------------------------------------------------------------
        scores = sorted(get_scores(), key=lambda x: x[0])
        scores = sorted(scores, key=lambda x: x[1], reverse=True)[:5]
        current_date = dt.datetime.now().strftime("%d.%m.%Y %H:%M")
        end_screen_img = pygame.image.load("game_assets/end_screen.png")

        while end_screen:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    end_screen = False
                    global_running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    cur.execute("""INSERT OR REPLACE INTO scores(date, score) VALUES(?, ?)""", [current_date, money])
                    con.commit()
                    end_screen = False

            screen.blit(end_screen_img, (0, 0))
            for i, score in enumerate(scores):
                render(screen, pygame.font.SysFont("Arial", 40),
                       f"{i + 1}) date: {scores[i][0]}, score: {str(scores[i][1])}", "white", (20, 120 + 50 * i))
            render(screen, pygame.font.SysFont("Arial", 100), str(money), 'white', (725, 150))
            render(screen, pygame.font.SysFont("Times New Roman", 50), "Click anywhere", "white", (630, 290))
            render(screen, pygame.font.SysFont("Times New Roman", 50), "to save", "white", (710, 350))
            if pygame.mouse.get_focused():
                if any(pygame.mouse.get_pressed()):
                    screen.blit(cursor_select, pygame.mouse.get_pos())
                else:
                    screen.blit(cursor, pygame.mouse.get_pos())
            pygame.display.flip()
pygame.quit()
con.close()
