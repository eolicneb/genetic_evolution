class Cuerpo(object):
    def __init__(self, nombre="", ubicacion=None, giro=None, textura=None):
        self.nombre = nombre
        self.pos = ubicacion
        self.giro = giro
        self.tex = textura
    def DE(self, punto):
        punto = punto - self.pos
        if self.giro:
            punto = self.giro.desgiro(punto)
        return self.distancia(punto)
    def distancia(self, *args):
        return None
    def __str__(self):
        return "Cuerpo {}".format(self.nombre)

class Circo(Cuerpo):
    ''' Espacio circular pensado para contener 
    '''
    def __init__(self, radio=1.0, **kwargs):
        self.radio = radio
        super().__init__(**kwargs)
    def distancia(self, punto):
        return self.radio - punto.largo

class Planta(Cuerpo):
    ''' Espacio cuadrado para contener
    '''
    def __init__(self, lado=1.0, **kwargs):
        self.lado = lado
        super().__init__(**kwargs)
    def distancia(self, punto):
        return min([ self.lado - abs(i) for i in punto ])

class Ensamble(tuple):
    def DE(self, punto):
        return min([ solido.DE(punto) for solido in self ])

if __name__ == "__main__":

    import geom as g

    circo = Circo(radio=10, nombre="pista")
    print(circo)
    giro = g.Giro(((0.6, 0.8),(-0.8, 0.6)))
    punt = g.Punto((6, 6))
    print(giro.desgiro(punt))
    piso = Planta(lado=10.0, giro=g.Giro(((1, 1),0)))
    print("DE: {}".format(piso.DE(punt)))
    piso = Planta(lado=10.0, giro=g.Giro(((1, 1),0)))
    print("DE: {}".format(piso.DE(punt)))
    piso = Planta(lado=10.0, giro=g.Giro(((1, 1),0)))
    print("DE: {}".format(piso.DE(punt)))
