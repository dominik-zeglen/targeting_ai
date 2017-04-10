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
                                            init_speed=np.asarray(((random() - .5) * .5, random() * .3 + .8)) * 5))
            self.entities[asteroid].set('on_deregister', spawn_asteroid)
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
        running = True
        agent = Agent().fit(data)

        char = self.register(Controllable('sim/img/img1.png',
                                          self.screen,
                                          self,
                                          init_pos=(np.array((240, 420)))))

        scene = pg.image.load('sim/img/asteroids/scene.png')

        asteroid = spawn_asteroid()

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

            except SystemExit:
                running = False

            # AI
            if time() - learning_time > 5:
                agent = Agent().fit(data)
                learning_time = time()

            if time() - counter_time > (1. / bullets_per_second) * 60 / fps:
                counter_time = time()
                # a = agent.predict(np.hstack([np.asarray([_get_angle(self.get_entity(self.watcher.get(asteroid)).get('pos')),
                #                                          self.watcher.get(2)]).reshape(-1, 2)]))
                shoot_vec = (random(), random()) * np.array(self.res) - self.entities[char].pos
                shoot_vec = shoot_vec / sqrt(sum(shoot_vec ** 2))
                bullet_id = self.entities[char].fire(shoot_vec, 3.5)
                data[self.entities[bullet_id].get('sim_id')] = {
                    'shoot_pos': shoot_vec,
                    'ast_pos': None,
                    'hit': 0
                }
                bullet_counter += 1

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