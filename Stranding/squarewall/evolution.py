import squarewall as sq
from thinking import Brain

schema = (4, 5, 5, 4)
population = 50
reproductions = population // 3 + 1

class Window(object):
    width = 600
    height = 450

class RegisteredMov(sq.Movement):
    time_factor = 10
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.register = []
    def final(self):
        fin = super().final()
        self.register.append((self.loss(fin[1:3]),)+fin)
        # print(self.register[-1])
        return fin
    def loss(self, reg):
        return reg[0]*reg[0]+reg[1]*reg[1]*self.time_factor*self.time_factor

sq.Fauna.genes = [ Brain(schema=schema) for _ in range(population) ]
sq.Fauna.zoo = [ sq.Creature(movement=RegisteredMov(pos=[100,100], box=Window, brain=b)) for b in sq.Fauna.genes ]

dt = 5.
sq.Park.dt = dt
for iteration in range(5):
    print('Iteration ', iteration)

    for _ in range(100):
        sq.Movement.inc_t(dt)
        for c in sq.Fauna.zoo:
            c.move(dt)

    darwin = []
    for ix, c in enumerate(sq.Fauna.zoo):
        c.mov.final()
        print(c.name)
        c.mov.register.sort()
        darwin.append((c.mov.register[-1], ix))
        for reg in c.mov.register[:-3:-1]:
            print('  {:8.0f} {:4d} d={:8.3f} t={:6.3f}'.format(*reg))
    darwin.sort(reverse=True)
    # sq.Fauna.zoo[darwin[0][1]] = sq.Creature(movement=RegisteredMov(pos=[100,100], box=Window, brain=Brain(schema=schema)))
    # sq.Fauna.zoo[darwin[1][1]] = sq.Creature(movement=RegisteredMov(pos=[100,100], box=Window, brain=Brain(schema=schema)))
    for d in range(reproductions):
        sq.Fauna.zoo[darwin[d+reproductions][1]].mov.brain.layers = sq.Fauna.zoo[darwin[d][1]].mov.brain.layers
        sq.Fauna.zoo[darwin[d+reproductions][1]].mov.brain.mutate()
    for d in range(reproductions*2,population):
        sq.Fauna.zoo[darwin[d][1]] = sq.Creature(movement=RegisteredMov(pos=[100,100], box=Window, brain=Brain(schema=schema)))
    
sq.ParkApp().run()