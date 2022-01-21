import pygame
from math import degrees, atan2


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


def create_fonts(font_sizes_list):
    # Creates different fonts with one list
    fonts = []
    for size in font_sizes_list:
        fonts.append(
            pygame.font.SysFont("Arial", size))
    return fonts


def distance_between_two_points(p1, p2):
    return ((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) ** (1/2)

def angle_between_two_points(p1, p2):
    dy = p1[1] - p2[1]
    dx = p2[0] - p1[0]

    rads = atan2(dy, dx)
    degs = degrees(rads)
    if degs < 0:
        degs += 90

    return rads, degs