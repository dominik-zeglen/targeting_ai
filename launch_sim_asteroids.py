import pygame as pg
import numpy as np

from sim.sim import *
from pygame.locals import *
from time import time
from ai import Agent
from pickle import load, dump
from random import random
from math import sin, cos, sqrt, atan2, exp


class CustomSim(Sim):
    def loop(self):
        def spawn_asteroid():
            asteroid = self.register(Entity('sim/img/zybel.png',
                                            self.screen,
                                            self,
                                            init_pos=(_random_pos()),
                                            init_speed=np.asarray(((random() - .5) * .5, random() * .3 + .6)) * 3))
            self.entities[asteroid].appearance = pg.transform.scale(self.entities[asteroid].original,
                                                                    (np.asarray(
                                                                        self.entities[asteroid].original.get_size()) * (
                                                                         random() * .4 + 1)).astype('uint8'))
            # self.entities[asteroid].set('on_deregister', spawn_asteroid)
            self.type = 'asteroid'
            return self.watcher.update(0, self.entities[asteroid].sim_id)

        def _radial(pos, angle, center=[x / 2 for x in self.res], verbose=False):
            functions = [cos, sin]
            relational = pos - np.asarray(center)
            r = sqrt(sum((relational) ** 2))
            if verbose:
                print(r)
            curr_angle = atan2(relational[1], relational[0])

            return np.asarray([f(curr_angle + angle) * r for f in functions]) + center

        def _get_angle(pos, center=[x / 2 for x in self.res]):
            relational = pos - np.asarray(center)
            return atan2(relational[1], relational[0])

        def _random_pos():

            return self.res[0] * random(), 0

        def sigmoid(x):
            return 1 / (1 + exp(-x))

        data = None
        try:
            with open('sim/pickle_data/data.pck', 'rb+') as f:
                try:
                    data = load(f)
                except:
                    data = {}
        except:
            data = {'0': {
                'shoot_angle': 0,
                'ast_angle': 0,
                'ast_vel': 0,
                'hit': 1
            }}

        self.watcher = Watcher()
        # Asteroid sim_id
        self.watcher.objects.append(1)
        # Kill counter
        self.watcher.objects.append(0)
        # Asteroid velocity
        self.watcher.objects.append(0)
        # Sim data
        self.watcher.objects.append(data)

        pg.font.init()
        font = pg.font.SysFont('arial', 15)
        start_time = time()
        counter_time = time()
        learning_time = time()
        spawner_time = time()
        running = True
        agent = Agent().fit(data)

        char = self.register(Controllable('sim/img/img1.png',
                                          self.screen,
                                          self,
                                          init_pos=(np.array((240, 420)))))

        scene = pg.image.load('sim/img/asteroids/scene.png')

        shoot_pos = None
        bullets_per_second = 3
        bullet_counter = 1

        while running:
            try:
                for event in pg.event.get():
                    if event.type == pg.QUIT:
                        running = False

                    elif event.type == pg.KEYDOWN:
                        if event.key == pg.K_r:
                            self = Sim(self.res)
                            self.loop()
                            running = False

                    elif event.type == pg.MOUSEBUTTONDOWN:
                        if pg.mouse.get_pressed()[0]:
                            shoot_pos = pg.mouse.get_pos()
                            print(shoot_pos)

            except SystemExit:
                running = False

            # AI
            if time() - learning_time > 60:
                agent = Agent().fit(data)
                learning_time = time()

            if time() - counter_time > (1. / bullets_per_second) * 60 / fps:
                if shoot_pos:
                    counter_time = time()
                    # a = agent.predict(np.hstack([np.asarray([_get_angle(self.get_entity(self.watcher.get(asteroid)).get('pos')),
                    #                                          self.watcher.get(2)]).reshape(-1, 2)]))
                    shoot_vec = (np.asarray(shoot_pos) if shoot_pos else (random(), random()) * np.array(self.res)) - \
                                self.entities[char].pos
                    shoot_vec = shoot_vec / sqrt(sum(shoot_vec ** 2))
                    bullet_id = self.entities[char].fire(shoot_vec, 10)
                    data[self.entities[bullet_id].get('sim_id')] = {
                        'shoot_pos': shoot_vec,
                        'ast_pos': None,
                        'hit': 0
                    }
                    bullet_counter += 1
                    shoot_pos = None

            if time() - spawner_time > .5:
                spawner_time = time()
                if random() > .2 \
                        and len([1 for x in self.entities if x.type == 'asteroid']) < (time() - start_time) / 60 \
                        and len([1 for x in self.entities if x.type == 'asteroid']) < 8:
                    spawn_asteroid()

            self.clock.tick(fps)
            self.screen.fill(colors['white'])

            # Draw scene
            self.screen.blit(scene, (0, 0))

            # Draw FPS counter
            pg.draw.rect(self.screen, colors['black'], [400, 0, 480, 30])
            self.screen.blit(font.render(str(self.clock.get_fps()), 1, colors['white']), (400, 0))

            # Draw kill counter
            pg.draw.rect(self.screen, colors['black'], [0, 0, 80, 30])
            self.screen.blit(font.render(str(self.watcher.get(1) * 1. / bullet_counter), 1, colors['white']), (0, 0))

            self.sim()
            pg.display.flip()

            # with open('sim/pickle_data/data.pck', 'wb+') as f:
            #     print('Dumping')
            #     dump(data, f)


sim = CustomSim((480, 480))
sim.loop()
