import numpy as np
# from sklearn.tree import DecisionTreeRegressor as Model
# from sklearn.linear_model import HuberRegressor as Model
# from sklearn.linear_model import Ridge as Model
from sklearn.svm import SVR as Model
# from sklearn.neural_network import MLPRegressor as Model
# from sklearn.ensemble import RandomForestRegressor as Model
from time import time

import matplotlib.pyplot as plt


class Agent:
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

        print('Succesful hits data / Total hits data: %d / %d' % (len(train[:, 0]), len(data)))

        self.model.fit(train, values, sample_weight=weights)

        return self

    def predict(self, angle):
        return self.model.predict(angle)
