from flappyclass import *
import neat
import time

gen = 0

def draw_window(win, birds, pipes, base, score, gen):
    win.blit(BG_IMG, (0, 0))

    for pipe in pipes:
        pipe.draw(win)

    text = STAT_FONT.render("Score: " + str(score), 1, (255, 255, 255))
    win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))

    text = STAT_FONT.render("Gen: " + str(gen), 1, (255, 255, 255))
    win.blit(text, (10, 10))

    base.draw(win)
    
    for bird in birds:
        bird.draw(win)
    
    pygame.display.update()

def main(genomes, config):
    global gen  
    gen += 1
    spd = INIT_VEL
    # create game objects
    base = Base(730)
    pipes = [Pipe(spd, 700)]
    birds = []
    nets = []  # list of neural networks
    ge = [] # list of genomes
    
    timer = 0 # for increasing speed
    score = 0
    
    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        birds.append(Bird(230, 350))
        g.fitness = 0
        ge.append(g)
    
    print("at the start, there are {} birds".format(len(birds)))
    
    # create game window
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    
    # clock
    clock = pygame.time.Clock()
    
    # main game loop
    running = True
    while running:
        clock.tick(30) # fps

        # event check
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                quit()
        
        # find the bird that we suppose to look at
        pipe_idx = 0
        if len(birds) > 0: 
            for pipe in pipes:
                if not (birds[0].x > pipe.x + pipe.PIPE_TOP.get_width()):
                    break
                else:
                    pipe_idx += 1
        else: # abort generation if all birds are dead
            running = False
            break
        
        
        # move birds
        for i, bird in enumerate(birds):
            bird.move()
            ge[i].fitness += 0.1 # reward for surviving 
            
            output = nets[i].activate((bird.y, 
                                       abs(bird.y - pipes[pipe_idx].height), 
                                       abs(bird.y - pipes[pipe_idx].bot)))
            if output[0] > 0.5:
                    bird.jump()
        
        # update position
        add_pipe = False
        pipe_rem = []
        for pipe in pipes:
            for i, bird in enumerate(birds):
                if pipe.collide(bird): # dead
                    ge[i].fitness -= 1 # punish the bird that dies
                    
                    # kill the bird that hit the pipe
                    birds.pop(i)
                    nets.pop(i)
                    ge.pop(i)

                if not pipe.passed and pipe.x < bird.x: 
                    pipe.passed = True
                    add_pipe = True
                    
            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                pipe_rem.append(pipe)

            pipe.move()
        
        # remove out of screen pipes
        for r in pipe_rem:
            pipes.remove(r)
            
        if add_pipe:
            score += 1
            # reward the birds that passed
            for g in ge:
                g.fitness += 5
            pipes.append(Pipe(spd, 700))

        for i, bird in enumerate(birds):
            if bird.y + bird.img.get_height() >= 730 or bird.y < 0: # dead
                birds.pop(i)
                nets.pop(i)
                ge.pop(i)

        base.move()
        


        # draw 
        draw_window(win, birds, pipes, base, score, gen)

        # timer
        if timer < 10:
            timer += 0.1
        else:
            timer = 0
            spd = spd + 2 
            if spd < MAX_VEL:
                for pipe in pipes:
                    pipe.vel = spd
                base.vel = spd
            else:
                spd = MAX_VEL




def run(path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, 
                                neat.DefaultSpeciesSet, neat.DefaultStagnation, path)

    # population
    p = neat.Population(config)
    
    # stats reporter
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    
    winner = p.run(main, 50)

if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config.txt')
    run(config_path)
