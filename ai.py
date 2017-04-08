import numpy as np
# from sklearn.tree import DecisionTreeRegressor as Model
# from sklearn.linear_model import HuberRegressor as Model
# from sklearn.linear_model import Ridge as Model
from sklearn.svm import SVR as Model

import matplotlib.pyplot as plt


class Agent:
    def __init__(self):
        self.model = Model()

    def fit(self, data):
        train = []
        values = []
        weights = []
        for bullet_id, bullet in data.items():
            if bullet['hit']:
                train.append(bullet['ast_angle'])
                values.append(bullet['shoot_angle'])

        train = np.asarray(train).reshape(-1, 1)
        values = np.asarray(values).reshape(-1, 1)

        # plt.scatter(train, values)
        # plt.show()

        print(np.hstack([train, values]))

        self.model.fit(train, values)
        print(self.model.score(train, values))

        return self

    def predict(self, angle):
        return self.model.predict(angle)
