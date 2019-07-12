import numpy as np

class Brain(object):
    mutation_factor = 0.001
    def __init__(self, schema=(2,1)):
        self.schema = schema
        self.layers = []
        self.init_layers()
    def init_layers(self):
        sch = self.schema
        for i, o in zip(sch[:-1], sch[1:]):
            self.layers.append(np.random.rand(i+1, o) - .5)
            # print('layer: ', self.layers[-1])
    def think(self, input_):
        for lay in self.layers:
            input_ = np.append(input_, 1.) @ lay
            input_.clip(0)
        return input_
    @property
    def ADN(self):
        from itertools import chain
        return tuple(chain(*[lay.flatten() for lay in self.layers]))
    def load_ADN(self, ADN):
        self.layers, marker = [], 0
        for i, o in zip(self.schema[:-1], self.schema[1:]):
            self.layers.append(np.array(ADN[marker:marker+i*o+o]).reshape((i+1,o)))
            # print('last layer: ', self.layers[-1], np.array(ADN[marker:marker+i*o+o]).reshape((i+1,o)))
            marker += i*o+o
    def mutate(self):
        for lay in self.layers:
            lay *= 1 + np.random.randn(*lay.shape)*self.mutation_factor

if __name__ == '__main__':
    i = np.random.rand(5,1)
    brain = Brain(schema=(5,4,3,2))
    print('out: ', *brain.think(i))
    print('ADN: ', brain.ADN)
    brain.mutate()
    print('ADN: ', brain.ADN)

