import pygame
import neat
import time
import os
import random

# Window Size
WIN_WIDTH = 500
WIN_HEIGHT = 800

# Assets
BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("img", "bird1.png"))),
             pygame.transform.scale2x(pygame.image.load(os.path.join("img", "bird2.png"))),
             pygame.transform.scale2x(pygame.image.load(os.path.join("img", "bird3.png")))]
PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("img", "pipe.png")))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("img", "base.png")))
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("img", "bg.png")))


class Bird:
    IMGS = BIRD_IMGS
    MAX_ROTATION = 25
    ROTATION_VELOCITY = 20
    ANIMATION_TIME = 5

    # Starting position
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tilt = 0
        self.tick_count = 0 # Physics when jumping and falling
        self.velocity = 0
        self.height = self.y
        self.img_count = 0 # Keep track of animation
        self.img = self.IMGS[0]

    def jump(self):
        # (0, 0) is the top left part of the screen
        # To go up we need negative velocity
        # To go down we need positive velocity
        self.velocity = -10.5
        # Set tick_count to 0 to know when the bird
        # is changing direction / velocity
        self.tick_count = 0
        # Keep track where the bird was when jump was activated
        self.height = self.y

    def move(self):
        # Records a frame
        self.tick_count += 1
        # Calculate how much the bird is moving for each frame
        # Move up/down based on velocity
        displacement = self.velocity*self.tick_count + 1.5*self.tick_count**2

        # Failsafe, make sure velocity is not too high or low
        if displacement >= 16:
            displacement = 16
        if displacement < 0:
            displacement -= 2

        self.y = self.y + displacement

        # Tilt
        if displacement < 0 or self.y < self.height + 50:
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else:
            if self.tilt > -90:
                self.tilt -= self.ROTATION_VELOCITY

    def draw(self, window):
        self.img_count += 1

        # Check which image to show based on current image count
        if self.img_count < self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count < self.ANIMATION_TIME*2:
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME * 3:
            self.img = self.IMGS[2]
        elif self.img_count < self.ANIMATION_TIME * 4:
            self.img = self.IMGS[1]
        elif self.img_count == self.ANIMATION_TIME * 4 + 1:
            self.img = self.IMGS[0]
            self.img_count = 0

        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME*2

        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_image.get_rect(center=self.img.get_rect(topleft = (self.x, self.y)).center)
        window.blit(rotated_image, new_rect.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.img)

class Pipe:
    # The bird doesn't move, the pipes move towards the bird
    GAP = 200
    VELOCITY = 5

    def __init__(self, x):
        self.x = x
        self.height = 0

        # Keep track of where the top and bottom of the pipe are being drawn
        self.top = 0
        self.bottom = 0
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True)
        self.PIPE_BOTTOM = PIPE_IMG

        # Has the bird passed this pipe
        # Purposes for collision and AI
        self.passed = False
        self.set_height()

    def set_height(self):
        self.height = random.randrange(50, 450)
        # Purpose: Figure out where the top of the pipe should be
        # Have to figure out the top left position of the image
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP

    def move(self):
        self.x -= self.VELOCITY

    def draw(self, window):
        window.blit(self.PIPE_TOP, (self.x, self.top))
        window.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    def collide(self, bird):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

        # How far away these masks are to each other
        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        # Do the masks collide?
        b_point = bird_mask.overlap(bottom_mask, bottom_offset)
        t_point = bird_mask.overlap(top_mask, top_offset)

        # If either of them != None, then the bird has collided with pipes
        if t_point or b_point:
            return True

        return False


def draw_window(window, bird):
    window.blit(BG_IMG, (0,0))
    bird.draw(window)
    pygame.display.update()


def main():
    bird = Bird(200, 200)
    window = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pygame.time.Clock()

    run = True
    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        #bird.move()
        draw_window(window, bird)

    pygame.quit()
    quit()

if __name__ == '__main__':
    main()





