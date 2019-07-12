class Primitiva(object):
    def __init__(self, tupla):
        self.tup = tuple([ i for i in iter(tupla) ])
        self.len = len(self.tup)
    def __str__(self):
        return "(" + ", ".join([ "{}" for _ in range(self.len) ]).format(*self.tup) + ")"
    def __iter__(self):
        self.cont = 0
        return self
    def __next__(self):
        n = self.cont
        if n == self.len:
            raise StopIteration
        else:
            self.cont += 1
            return self.tup[n]

class Punto(Primitiva):
    def __sub__(self, otro):
        if otro == None:
            return self
        else:
            return Punto([ i - j for i, j in zip(self, otro) ])
    def __mul__(self, otro):
        if otro == None:
            return Punto((0, 0))
        if isinstance(otro, Primitiva):
            if isinstance(otro, Punto):
                return sum([ i * j for i, j in zip(self, otro) ])
        else:
            return Punto([ i * otro for i in self ])
    @property
    def largo(self):
        return sum([ e*e for e in self ])**0.5
    @property
    def versor(self):
        l = self.largo
        return Punto([ i / l for i in self ])
    @property
    def normal(self):
        i, j = self
        return Punto((-j, i))

class Giro(Primitiva):
    def __init__(self, tuplas):
        if isinstance(tuplas, Giro):
            super().__init__(Giro)
        else:
            if isinstance(tuplas, Punto):
                tuplas = tuplas.versor
            elif hasattr(tuplas, "__iter__") and hasattr(tuplas[0], "__iter__") and len(tuplas[0]) > 1:
                tuplas = Punto(tuplas[0][:2]).versor
            else:
                print("Acá pasó algo raro...")
            tuplas = (tuplas, tuplas.normal)
            super().__init__([ Punto(i) for i in iter(tuplas) ])
    @property
    def t(self):
        return Giro(zip(*self))
    def __call__(self, prim):
        if isinstance(prim, Punto):
            return Punto([ i * prim for i in self.t ])
        elif isinstance(prim, Giro):
            return Giro([ [ i * j for i in self.t ] for j in prim ])
    def desgiro(self, punto):
        return Punto([ i * punto for i in self ])