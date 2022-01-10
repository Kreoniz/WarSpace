import pygame


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
