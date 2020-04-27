import pygame
import neat
import time
import os
import random
pygame.font.init()

GEN = 0

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

STAT_FONT = pygame.font.SysFont("comicsans", 50)


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
        self.tick_count = 0  # Physics when jumping and falling
        self.velocity = 0
        self.height = self.y
        self.img_count = 0  # Keep track of animation
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
        displacement = self.velocity * self.tick_count + 1.5 * self.tick_count ** 2

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
        elif self.img_count < self.ANIMATION_TIME * 2:
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
            self.img_count = self.ANIMATION_TIME * 2

        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_image.get_rect(center=self.img.get_rect(topleft=(self.x, self.y)).center)
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


class Base:
    VELOCITY = 5
    WIDTH = BASE_IMG.get_width()
    IMG = BASE_IMG

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        self.x1 -= self.VELOCITY
        self.x2 -= self.VELOCITY

        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH

        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, window):
        window.blit(self.IMG, (self.x1, self.y))
        window.blit(self.IMG, (self.x2, self.y))


def draw_window(window, birds, pipes, base, score,gen):
    window.blit(BG_IMG, (0, 0))

    for pipe in pipes:
        pipe.draw(window)
    text = STAT_FONT.render("Score: " + str(score), 1, (255, 255, 255))
    window.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))

    text = STAT_FONT.render("Gen: " + str(gen), 1, (255, 255, 255))
    window.blit(text, (10, 10))
    base.draw(window)
    for bird in birds:
        bird.draw(window)
    pygame.display.update()


def main(genomes, config):
    global GEN
    GEN += 1
    nets = []
    ge = []
    birds = []

    # Genome is tuple that has the genome ID and genome object
    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        birds.append(Bird(230, 350))
        g.fitness = 0
        ge.append(g)

    base = Base(730)
    pipes = [Pipe(700)]
    window = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pygame.time.Clock()
    score = 0

    run = True
    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

        pipe_ind = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
                pipe_ind = 1
        else:
            run = False
            break

        for x, bird in enumerate(birds):
            bird.move()
            ge[x].fitness += 0.1

            output = nets[x].activate((bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom)))

            if output[0] > 0.5:
                bird.jump()

        # bird.move()
        add_pipe = False
        rem = []
        for pipe in pipes:
            for x, bird in enumerate(birds):
                # Check if every pipe collides with every bird
                if pipe.collide(bird):
                    ge[x].fitness -= 1
                    birds.pop(x)
                    nets.pop(x)
                    ge.pop(x)

                # If pipe has been passed
                if not pipe.passed and pipe.x < bird.x:
                    pipe.passed = True
                    add_pipe = True

            # If pipe is completely off the screen
            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)

            pipe.move()

        if add_pipe:
            score += 1
            for g in ge:
                g.fitness += 5
            pipes.append(Pipe(600))

        # Remove passed pipes
        for passed_pipe in rem:
            pipes.remove(passed_pipe)

        for x, bird in enumerate(birds):
            # Check if bird hit the ground
            # Prevent birds from flying over the visible window
            if bird.y + bird.img.get_height() > 730 or bird.y < 0:
                birds.pop(x)
                nets.pop(x)
                ge.pop(x)

        if score > 50:
            break

        base.move()
        draw_window(window, birds, pipes, base, score, GEN)


def run(config_file):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_file)
    population = neat.Population(config)
    population.add_reporter(neat.StdOutReporter(True))
    population.add_reporter(neat.StatisticsReporter())

    winner = population.run(main, 50)


if __name__ == '__main__':
    # Determine path to configuration file. This path manipulation is
    # here so that the script will run successfully regardless of the
    # current working directory.
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward.txt')
    run(config_path)
