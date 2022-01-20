import pygame

all_sprites = pygame.sprite.Group()
tower_group = pygame.sprite.Group()

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

    def return_type(self):
        return self.type

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
        self.image = self.frames[8]