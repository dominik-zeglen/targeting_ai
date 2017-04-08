import numpy as np
# from sklearn.tree import DecisionTreeRegressor as Model
# from sklearn.linear_model import HuberRegressor as Model
# from sklearn.linear_model import Ridge as Model
# from sklearn.svm import SVR as Model
# from sklearn.neural_network import MLPRegressor as Model
from sklearn.ensemble import RandomForestRegressor as Model

import matplotlib.pyplot as plt


class Agent:
    def __init__(self):
        self.model = Model(n_estimators=100)

    def fit(self, data):
        train = []
        values = []
        weights = []
        counter = 0
        for bullet_id, bullet in data.items():
            if bullet['hit']:
                train.append([bullet['ast_angle'], bullet['ast_vel']])
                values.append(bullet['shoot_angle'])
                weights.append(counter)
                counter = 0
            else:
                counter += .1

        train = np.asarray(train).reshape(-1, 2)
        values = np.asarray(values).reshape(-1, 1)

        # plt.hist(train[:, 0] * 360 / 3.141 / 2, bins=24)
        # plt.show()

        print('Succesful hits data / Total hits data: %d / %d' % (len(train[:, 0]), len(data)))

        self.model.fit(train, values, sample_weight=weights)

        return self

    def predict(self, angle):
        return self.model.predict(angle)
