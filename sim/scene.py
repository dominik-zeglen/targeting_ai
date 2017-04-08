import pygame as pg
import numpy as np

from pygame.locals import *
from time import time
from random import random
from math import sin, cos, sqrt, atan2, exp
from pickle import load, dump
from ai import Agent

res = (480, 480)
fps = 30
colors = {
    'black': (0, 0, 0),
    'white': (255, 255, 255)
}

data = None
try:
    with open('sim/pickle_data/data.pck', 'rb+') as f:
        try:
            data = load(f)
        except:
            data = {}
except:
    data = {'0' : {
        'shoot_angle': 0,
        'ast_angle': 0,
        'hit': 1
    }}
data_init_len = len(data)


class Entity:
    def __init__(self, *args, **kwargs):
        # img_path, parent, init_pos = (0, 0), init_rot = 0, init_scale = 1, init_speed = (0, 0)
        self.original = pg.image.load(args[0])
        self.appearance = self.original
        self.parent = args[1]
        self.sim = args[2]
        self.sim_id = None
        self.pos = np.asarray(kwargs['init_pos']) - np.asarray(self.original.get_size()) / 2
        self.rot = kwargs['init_rot'] if 'init_rot' in kwargs else 0
        self.scale = kwargs['init_scale'] if 'init_scale' in kwargs else 0
        self.speed = np.asarray(kwargs['init_speed']) if 'init_speed' in kwargs else np.asarray((0, 0))
        self.hit_radius = sqrt(sum((np.asarray(self.original.get_size()) / 2) ** 2))

        self.on_deregister = lambda: None
        self.displayable = True

    def update(self):
        if self.displayable:
            self.pos += self.speed
        return self

    def set(self, attr, value):
        setattr(self, attr, value)
        return self

    def get(self, attr):
        return getattr(self, attr)

    def display(self):
        if self.displayable:
            self.parent.blit(self.appearance, self.pos)


class Bullet(Entity):
    def check_alive(self):
        if sum([True if coord > r or coord < 0 else False for coord, r in zip(self.pos, res)]):
            self.sim.deregister(self.sim_id)
            return False

        for entity in self.sim.entities:
            if not isinstance(entity, Controllable) and not isinstance(entity, Bullet):
                if sqrt(sum((entity.get('pos') - self.pos + np.asarray(
                        self.appearance.get_size()) / 2) ** 2)) <= entity.get('hit_radius'):
                    self.sim.deregister(self.sim_id)
                    self.sim.deregister(entity.sim_id)
                    data[data_init_len + self.sim_id]['hit'] = 1
                    return entity.sim_id


class Controllable(Entity):
    def fire(self, angle, bullet_speed):
        fs = [cos, sin]
        direction = [f(angle) * bullet_speed for f in fs]
        return self.sim.register(Bullet('sim/img/bullet.png',
                                        self.parent,
                                        self.sim,
                                        init_pos=(self.pos + [x / 2 for x in self.original.get_size()]),
                                        init_speed=direction))


class Watcher:
    def __init__(self):
        self.objects = []

    def add(self, o):
        self.objects.append(o)
        return len(self.objects) - 1

    def update(self, index, value):
        self.objects[index] = value
        return index

    def get(self, index):
        return self.objects[index]


class Sim:
    def __init__(self, res):
        self.res = res
        self.screen = pg.display.set_mode(res)
        self.clock = pg.time.Clock()
        self.entities = [Entity('sim/img/img1.png',
                                self.screen,
                                self,
                                init_pos=(np.array((240, 240))))]
        self.entities[0].set('displayable', False)
        self.entities[0].set('hit_radius', 0)
        self.entities[0].set('sim_id', 0)
        self.id_counter = 1

    def register(self, entity):
        self.entities.append(entity)
        entity.set('sim_id', self.id_counter)
        self.id_counter += 1
        return len(self.entities) - 1

    def deregister(self, index):
        id = [i for i, x in enumerate(self.entities) if x.sim_id == index][0]
        self.entities[id].on_deregister()
        self.entities.pop(id)

    def sim(self):
        for entity in self.entities:
            entity.update().display()
            if isinstance(entity, Bullet):
                entity.check_alive()

    def get_entity(self, index):
        l = [i for i, x in enumerate(self.entities) if x.sim_id == index]
        id = l[0] if len(l) else 0
        return self.entities[id]

    def loop(self):
        def spawn_asteroid():
            asteroid = self.register(Entity('sim/img/zybel.png',
                                            self.screen,
                                            self,
                                            init_pos=(_radial(np.array((240, 240)) - (120, 0) - (16, 16), random() * 2 * 3.141))))
            self.entities[asteroid].set('on_deregister', spawn_asteroid)
            watcher.update(1, watcher.get(1) + 1)
            return watcher.update(0, self.entities[asteroid].sim_id)

        watcher = Watcher()
        watcher.objects.append(1)
        watcher.objects.append(0)

        pg.font.init()
        start_time = time()
        counter_time = time()
        running = True

        char = self.register(Controllable('sim/img/img1.png',
                                          self.screen,
                                          self,
                                          init_pos=(np.array((240, 240)))))

        asteroid = spawn_asteroid()

        ast_speed = .4
        bullets_per_second = 2
        bullet_counter = 1
        agent = Agent().fit(data)

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
            if time() - counter_time > 1. / bullets_per_second:
                counter_time = time()
                a = agent.predict(np.asarray([_get_angle(self.get_entity(watcher.get(asteroid)).get('pos'))]).reshape(-1, 1))
                # a = random() * 3.141 * 2
                bullet_id = self.get_entity(char).fire(a, 7)
                data[data_init_len + self.entities[bullet_id].get('sim_id')] = {
                    'shoot_angle': a,
                    'ast_angle': _get_angle(self.get_entity(watcher.get(asteroid)).get('pos')),
                    'hit': 0
                }
                bullet_counter += 1

            self.clock.tick(fps)
            self.screen.fill(colors['white'])

            # Draw helper lines
            pg.draw.line(self.screen, colors['black'], [0, 240], [480, 240])
            pg.draw.line(self.screen, colors['black'], [240, 0], [240, 480])
            pg.draw.circle(self.screen, colors['black'], [240, 240], 136, 2)

            # Draw FPS counter
            pg.draw.rect(self.screen, colors['black'], [400, 0, 480, 30])
            font = pg.font.SysFont('arial', 15)
            self.screen.blit(font.render(str(self.clock.get_fps()), 1, colors['white']), (400, 0))

            # Draw kill counter
            pg.draw.rect(self.screen, colors['black'], [0, 0, 80, 30])
            font = pg.font.SysFont('arial', 15)
            self.screen.blit(font.render(str(watcher.get(1) * 1. / bullet_counter), 1, colors['white']), (0, 0))

            self.get_entity(watcher.get(asteroid)).set('pos',
                                                       _radial(self.get_entity(watcher.get(asteroid)).get('pos'),
                                                               2 * 3.141 / fps * ast_speed) )

            self.sim()
            pg.display.flip()

        # with open('sim/pickle_data/data.pck', 'wb+') as f:
        #     print('Dumping')
        #     dump(data, f)


def _radial(pos, angle, center=[x / 2 for x in res]):
    functions = [cos, sin]
    relational = pos - np.asarray(center) + (16, 16)
    r = sqrt(sum((relational) ** 2))
    curr_angle = atan2(relational[1], relational[0])

    return np.asarray([f(curr_angle + angle) * r for f in functions]) + center - (16, 16)


def _get_angle(pos, center=[x / 2 for x in res]):
    relational = pos - np.asarray(center)
    return atan2(relational[1], relational[0])


def sigmoid(x):
    return 1 / (1 + exp(-x))


def print_hit():
    print("NOT DOGED")
