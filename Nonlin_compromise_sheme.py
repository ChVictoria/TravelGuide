import numpy as np


class Convolution:
    def __init__(self, data, coeff):
        self.data = data
        self.coeff = coeff

    def min_max_transform(self):
        for i in range(len(self.data)):
            if self.data[i][len(self.data[i])-1] == 'max':
                for j in range(len(self.data[i])-1):
                    self.data[i][j] = 1 / self.data[i][j]
        self.data = np.delete(self.data, len(self.data[0])-1, 1)

    def normalize(self, array):
        return array / sum(array)

    def integrated_score(self):
        self.min_max_transform()
        self.coeff = self.normalize(self.coeff)

        for i in range(len(self.data)):
            self.data[i] = self.normalize(self.data[i])

        self.score = np.zeros(len(self.data[0]))
        for i in range(len(self.data[0])):
            for j in range(len(self.data)):
                self.score[i] += self.coeff[j]/(1-self.data[j][i])

        return self.score

    def optimum(self):
        return np.where(self.score == min(self.score))[0][0]
