from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty, NumericProperty, ListProperty
from kivy.graphics import PushMatrix, PopMatrix, Rotate

class Pasos():
    def __init__(self, dt=1.0, f=1.0, A=1.0, centros=((0,0),(0,0))):
        self.t = 0.0
        self.dt = dt
        self.f = f
        self.A = A
        self.c = centros
    def __call__(self):
        from math import sin, cos
        a, A, c = self.t*self.f, self.A, self.c
        self.t += self.dt
        return ((A*sin(a)+c[0][0], A*cos(a)+c[0][1]), 
                (-A*cos(a)+c[1][0], A*sin(a)+c[1][1]))

paseo = [ Pasos(A=10.0, f=1.2, centros=((-50,0),(50,0))),
          Pasos(A=10.0, f=1.2, centros=((0,-50),(0,50))) ]

class Foot(Widget):
    def move(self, step, root):
        self.center_x = root.trunk.center_x + step[0]
        self.center_y = root.trunk.center_y + step[1]

class Muscle(Widget):
    width = NumericProperty(5)
    length = NumericProperty(100)
    p = ListProperty()
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        p = self.p
        self.length = 100 if len(p) < 4 else ((p[2]-p[0])**2+(p[1]-p[3])**2)**0.5
        self.width = 500 / self.length
    def move(self, *args):
        print(self.p)

class Body(Widget):
    pass

class Creature(Widget):
    trunk = ObjectProperty(None)
    lFoot = ObjectProperty(None)
    rFoot = ObjectProperty(None)
    muscle = ObjectProperty(None)
    muscle2 = ObjectProperty(None)
    head = ObjectProperty(None)
    heap = ObjectProperty(None)
    vel = NumericProperty(-1.0)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # self.head.center_x = self.center_x
        # self.head.center_y = self.center_y + 50
        # self.heap.center_x = self.center_x
        # self.heap.center_y = self.center_y - 50
        # print(self.head.center)
        # print(self.heap.center)
        # self.muscle2.p = self.heap.center + self.head.center
        # self.add_widget(self.head)
        # self.add_widget(self.heap)
        # self.add_widget(self.muscle2)
    def move(self):
        if self.x <= -300 or self.x > 300: self.vel = -self.vel
        self.x += self.vel
        pasos1, pasos2 = paseo[0](), paseo[1]()
        self.lFoot.move(pasos1[0], self)
        self.rFoot.move(pasos1[1], self)
        # self.head.move(pasos2[0], self)
        # self.heap.move(pasos2[1], self)
        # self.muscle2.p = self.head.center+self.heap.center

class Park(BoxLayout):
    bicho = ObjectProperty(None)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_interval(self.update, 0.05)
    def update(self, dt):
        self.bicho.move()

Park.bicho2 = Foot()
Park.bicho2.pos = (100, 100)

class RunField(App):
    def build(self):
        return Builder.load_file('creature.kv')
RunField().run()
