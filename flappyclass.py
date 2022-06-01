import pygame
import os
import random

pygame.font.init()

# constants
WIN_WIDTH = 500
WIN_HEIGHT = 800

STAT_FONT = pygame.font.SysFont("comicsans", 40)

# pipe and base
INIT_VEL = 5
MAX_VEL = 20

# birds
G = 6
BIRD_VEL = 12
MAX_FALL = 18

BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird1.png'))),
             pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird2.png'))),
             pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird3.png')))
             ]

PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'pipe.png')))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'base.png')))
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bg.png')))

# classes

class Bird:
    # constants
    IMGS = BIRD_IMGS
    MAX_ROTATION = 25
    ROT_VEL = 20
    ANIMATION_TIME = 5

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tilt = 0

        self.tick_count = 0

        self.vel = 0
        self.height = self.y

        self.img_count = 0
        self.img = self.IMGS[0]

    def jump(self):
        self.vel = -BIRD_VEL
        self.tick_count = 0  # keep track of when we last jumped
        self.height = self.y

    def move(self):
        self.tick_count += 1
        # displacement: d = vt + 0.5 * gt^2
        d = self.vel * self.tick_count + 0.5 * G *self.tick_count ** 2

        # cap displacement
        if d >= MAX_FALL:
            d = MAX_FALL

        if d < 0:
            d -= 2

        # moving the bird
        self.y += d

        # tilting the bird
        if d < 0 or self.y < self.height + 50:
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else:
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL

    def draw(self, win):
        self.img_count += 1

        # one animation cycle
        if self.img_count < self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count < self.ANIMATION_TIME * 2:
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME * 3:
            self.img = self.IMGS[2]
        elif self.img_count < self.ANIMATION_TIME * 4:
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME * 4 + 1:
            self.img = self.IMGS[0]
            self.img_count = 0 # reset cycle
            
        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME * 2

        # rotate the image
        rotated_img = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_img.get_rect(center=self.img.get_rect(topleft=(self.x, self.y)).center)

        # draw the image to the screen
        win.blit(rotated_img, new_rect.topleft)
        
    def get_mask(self): # get collision mask
        return pygame.mask.from_surface(self.img)

class Pipe:
    GAP = 230
    
    def __init__(self, vel, x):
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True)
        self.PIPE_BOTTOM = PIPE_IMG
        
        self.x = x
        self.height = 0
        
        self.vel = vel
        
        self.top = 0
        self.bot = 0
        
        self.passed = False
        self.set_height()
        
    def set_height(self):
        self.height = random.randrange(100, 400)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bot = self.height + self.GAP        

    def move(self):
        self.x -= round(self.vel)
        
    def draw(self, win):
        win.blit(self.PIPE_TOP, (self.x, self.top))
        win.blit(self.PIPE_BOTTOM, (self.x, self.bot))

    def collide(self, bird):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bot_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)
        
        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bot_offset = (self.x - bird.x, self.bot - round(bird.y))
        
        b_point = bird_mask.overlap(bot_mask, bot_offset)
        t_point = bird_mask.overlap(top_mask, top_offset)

        if b_point or t_point: # collided
            return True
        
        return False    
    
class Base:
    WIDTH = BASE_IMG.get_width()
    IMG = BASE_IMG
    
    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH
        self.vel = INIT_VEL
        
    def move(self):
        self.x1 -= round(self.vel)
        self.x2 -= round(self.vel)
        
        # out of screen
        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH
        
        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win):
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))



