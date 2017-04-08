import pygame as pg
import numpy as np

from pygame.locals import *
from time import time
from random import random
from math import sin, cos, sqrt, atan2, exp

res = (480, 480)
fps = 20
colors = {
    'black': (0, 0, 0),
    'white': (255, 255, 255)
}


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
        for entity in self.sim.entities:
            if not isinstance(entity, Controllable) and not isinstance(entity, Bullet):
                if sqrt(sum((entity.get('pos') - self.pos) ** 2)) <= entity.get('hit_radius'):
                    self.sim.deregister(self.sim_id)
                    self.sim.deregister(entity.sim_id)
                    break


class Controllable(Entity):
    def fire(self, angle, bullet_speed):
        fs = [cos, sin]
        direction = [f(angle) * bullet_speed for f in fs]
        return self.sim.register(Bullet('sim/img/bullet.png',
                                        self.parent,
                                        self.sim,
                                        init_pos=(self.pos + [x / 2 for x in self.original.get_size()]),
                                        init_speed=direction))


class Sim:
    def __init__(self, res):
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
        counter_time = time()
        running = True

        char = self.register(Controllable('sim/img/img1.png',
                                          self.screen,
                                          self,
                                          init_pos=(np.array((240, 240)))))
        asteroid = self.register(Entity('sim/img/img1.png',
                                        self.screen,
                                        self,
                                        init_pos=(np.array((240, 240)) - (120, 0))))
        self.get_entity(asteroid).set('on_deregister', print_hit)
        ast_speed = .3

        angles = []
        speeds = [0]
        decisions = []
        hit = []

        while running:
            try:
                for event in pg.event.get():
                    if event.type == pg.QUIT:
                        running = False
            except SystemExit:
                running = False

            self.clock.tick(fps)
            if time() - counter_time > .25:
                counter_time += .25
                if self.get_entity(asteroid).get('displayable'):
                    a = (_get_angle(self.get_entity(asteroid).get('pos')))
                    self.get_entity(char).fire(a, 7)
            self.screen.fill(colors['white'])
            pg.draw.line(self.screen, colors['black'], [0, 240], [480, 240])
            pg.draw.line(self.screen, colors['black'], [240, 0], [240, 480])

            ast_speed = ast_speed if random() > .025 else -ast_speed
            self.get_entity(asteroid).set('pos',
                                          _radial(self.get_entity(asteroid).get('pos'), 2 * 3.141 / fps * ast_speed))

            self.sim()
            angles.append(_get_angle(self.get_entity(asteroid).get('pos')))
            pg.display.flip()


def _radial(pos, angle, center=[x / 2 for x in res]):
    functions = [cos, sin]
    relational = pos - center
    r = sqrt(sum((relational) ** 2))
    curr_angle = atan2(relational[1], relational[0])

    return np.asarray([f(curr_angle + angle) * r for f in functions]) + center


def _get_angle(pos, center=[x / 2 for x in res]):
    relational = pos - center
    return atan2(relational[1], relational[0])


def sigmoid(x):
    return 1 / (1 + exp(-x))


def print_hit():
    print("NOT DOGED")
