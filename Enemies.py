import pygame
all_sprites = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()


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
