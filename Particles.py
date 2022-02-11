import pygame, sys, random

pygame.init()
def load_image(name, colorkey=None):
    try:
        image = pygame.image.load(name)
        if colorkey is not None:
            image = image.convert()
            if colorkey == -1:
                colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey)
        else:
            image = image.convert_alpha()
        return image
    except:
        print(f"Файл с изображением '{name}' не найден")
        sys.exit()

GRAVITY = 0.2
width, height = pygame.display.get_window_size()
screen_rect = (0, 0, width, height)

class Particle(pygame.sprite.Sprite):
    # сгенерируем частицы разного размера
    fire = [load_image("game_assets/vfx/spark.png")]
    for scale in (8, 9, 10):
        fire.append(pygame.transform.scale(fire[0], (scale, scale)))
    fire.pop(0)

    def __init__(self, pos, dx, dy):
        super().__init__(all_sprites, particle_group)
        self.image = random.choice(self.fire)
        self.rect = self.image.get_rect()

        # у каждой частицы своя скорость — это вектор
        self.velocity = [dx, dy]
        # и свои координаты
        self.rect.x, self.rect.y = pos

        # гравитация будет одинаковой (значение константы)
        self.gravity = GRAVITY

    def update(self):
        # применяем гравитационный эффект:
        # движение с ускорением под действием гравитации
        self.velocity[1] += self.gravity
        # перемещаем частицу
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        # убиваем, если частица ушла за экран
        if not self.rect.colliderect(screen_rect):
            self.kill()


def create_particles(position):
    # количество создаваемых частиц
    particle_count = 1
    # возможные скорости
    numbers = range(-2, 3)
    for _ in range(particle_count):
        Particle(position, random.choice(numbers), random.choice(numbers))

all_sprites = pygame.sprite.Group()
particle_group = pygame.sprite.Group()

# clock = pygame.time.Clock()
# running = True
# while running:
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             running = False
#         if event.type == pygame.MOUSEBUTTONDOWN:
#             # создаём частицы по щелчку мыши
#             create_particles(pygame.mouse.get_pos())
#
#     all_sprites.update()
#     screen.fill((0, 0, 0))
#     all_sprites.draw(screen)
#     pygame.display.flip()
#     clock.tick(50)
#
# pygame.quit()