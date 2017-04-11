import pygame as pg
import numpy as np

from math import sin, cos, sqrt, atan2, exp
from uuid import uuid4

fps = 30 * 2
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
        self.type = None

        self.on_deregister = lambda x: None
        self.on_hit = lambda x, y: None
        self.displayable = True

    def update(self):
        if self.displayable:
            self.pos += self.speed
        return self

    def set(self, attr, value):
        setattr(self, attr, value)
        return self

    def get(self, attr):
        if isinstance(attr, list) or isinstance(attr, tuple):
            return [getattr(self, x) for x in attr]
        return getattr(self, attr)

    def display(self):
        if self.displayable:
            self.parent.blit(self.appearance, self.pos)

    def check_alive(self):
        if sum([True if coord > r or coord < -s else False for coord, r, s in zip(self.pos, self.sim.res, self.appearance.get_size())]):
            self.sim.deregister(self.sim_id)
            return False
        else:
            return True


class Bullet(Entity):
    def check_alive(self):
        if sum([True if coord > r or coord < 0 else False for coord, r in zip(self.pos, self.sim.res)]):
            self.sim.deregister(self.sim_id)
            return False

        for entity in self.sim.entities:
            if not isinstance(entity, Controllable) and not isinstance(entity, Bullet):
                if sqrt(sum((entity.get('pos') - self.pos + np.asarray(
                        self.appearance.get_size()) / 2) ** 2)) <= entity.get('hit_radius'):
                    entity.on_hit(self.sim_id, entity.sim_id)

                    return entity.sim_id

        return True


class Controllable(Entity):
    def fire(self, fire_data, bullet_speed):
        if isinstance(fire_data, float):
            fs = [cos, sin]
            direction = [f(fire_data) * bullet_speed for f in fs]
        elif isinstance(fire_data, np.ndarray):
            direction = fire_data * bullet_speed
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
        self.watcher = None
        self.entities = [Entity('sim/img/img1.png',
                                self.screen,
                                self,
                                init_pos=(np.array((240, 240))))]
        self.entities[0].set('displayable', False)
        self.entities[0].set('hit_radius', 0)
        self.entities[0].set('sim_id', 0)

    def register(self, entity):
        self.entities.append(entity)
        entity.set('sim_id', str(uuid4()))
        return len(self.entities) - 1

    def deregister(self, index):
        id = [i for i, x in enumerate(self.entities) if x.sim_id == index][0]
        self.entities[id].on_deregister(self.entities[id])
        self.entities.pop(id)

    def sim(self):
        for entity in self.entities:
            entity.update().display()
            entity.check_alive()

    def get_entity(self, index):
        l = [i for i, x in enumerate(self.entities) if x.sim_id == index]
        id = l[0] if len(l) else 0
        return self.entities[id]

    def loop(self):
        pass
