import numpy as np
# from sklearn.tree import DecisionTreeRegressor as Model
# from sklearn.linear_model import HuberRegressor as Model
# from sklearn.linear_model import Ridge as Model
from sklearn.svm import SVR as Model
# from sklearn.neural_network import MLPRegressor as Model
# from sklearn.ensemble import RandomForestRegressor as Model
from sklearn.preprocessing import Normalizer
from time import time
from copy import deepcopy as dc

import matplotlib.pyplot as plt


class AgentZybel:
    def __init__(self):
        self.model = Model(degree=2)

    def fit(self, data):
        train = []
        values = []
        weights = []
        missed = []
        counter = 0
        for bullet_id, bullet in data.items():
            if bullet['hit']:
                train.append([bullet['ast_angle'], bullet['ast_vel']])
                values.append(bullet['shoot_angle'])
                weights.append(counter)
                counter = 0
            else:
                counter += .1
                missed.append(bullet['ast_angle'])

        train = np.asarray(train).reshape(-1, 2)
        values = np.asarray(values).reshape(-1, 1)
        missed = np.asarray(missed)

        if False:
            plt.hist(missed * 360 / 3.141 / 2, bins=24)
            plt.savefig('sim/img/plots/%d.jpg' % time())
            plt.clf()

        self.model.fit(train, values, sample_weight=weights)

        print('Succesful hits data / Total hits data: %d / %d' % (len(train[:, 0]), len(data)))
        print('Expected accuracy: %.2f' % self.model.score(train, values))

        return self

    def predict(self, angle):
        return self.model.predict(angle)


class AgentAsteroids:
    def __init__(self):
        self.model_x = Model(degree=2)
        self.model_y = Model(degree=2)
        self.norm_x = None
        self.norm_y = None

    def fit(self, data):
        train = []
        values = []
        weights = []
        missed = []
        counter = 0

        data_b = dc(data)

        for bullet_id, bullet in data.items():
            if bullet['hit'] and bullet['n_asteroid_id'] == bullet['hit_asteroid_id']:
                train.append([*bullet['n_asteroid_pos'], *bullet['n_asteroid_speed']])
                values.append(bullet['shoot_pos'])
                weights.append(counter)
                counter = 0
            else:
                counter += .1
                del data_b[bullet_id]

        data = data_b

        train = np.asarray(train).reshape(-1, 4)
        values = np.asarray(values).reshape(-1, 2)

        self.norm_x = Normalizer()
        self.norm_y = Normalizer()

        train = self.norm_x.fit_transform(train)
        values = self.norm_x.fit_transform(values)

        missed = np.asarray(missed)

        self.model_x.fit(train, values[:, 0], sample_weight=weights)
        self.model_y.fit(train, values[:, 1], sample_weight=weights)

        return self

    def predict(self, pos, speed):
        y = self.norm_x.transform(np.array([*pos, *speed]).reshape(1, 4))
        ret = np.asarray([self.model_x.predict(y)[0], self.model_y.predict(y)[0]])
        print('Aiming at: %s' % ret)
        return ret
