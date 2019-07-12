from kivy.app import App
from kivy.core.window import Window
from kivy.uix.floatlayout import FloatLayout
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty, NumericProperty, ListProperty, DictProperty

class Movement(object):
    box=None
    t = 0
    @classmethod
    def inc_t(cls, dt):
        cls.t += dt
    @staticmethod
    def xy_from_polar(r, a):
        from math import sin, cos
        return (r * cos(a), r*sin(a))
    def __init__(self, n=2, radio=500, vel=100, amp=50, frec=1., box=None):
        from random import random
        # pi = 180
        self.radio = radio
        self.f = frec
        self.amp = amp
        self.box = box
        self.pos = ( random() * box.width, random() * box.height )
        self.vel = tuple([ (random() - 0.5) * vel for _ in range(2) ])
        self.set_n(n)
    def set_n(self, n):
        from random import random
        from numpy.random import normal
        from math import pi
        radio = self.radio
        self.n = n
        self.theta = tuple([ random() * 2 * pi for _ in range(n) ])
        self.alfa =  tuple([ self.xy_from_polar(r, 2 * pi * (i // 2) / n + pi * (i%2)) for i, r in enumerate(normal(radio, radio/10., n)) ])
    def __call__(self, dt=1.):
        self.pos = ( (self.pos[0] + self.vel[0]*dt) % self.box.width, (self.pos[1] + self.vel[1]*dt) % self.box.height )
        orbits = ( self.xy_from_polar(self.amp, self.t * self.f + self.theta[i]) for i in range(self.n) )
        orb_alf = zip(orbits, self.alfa)
        return { 'pos':self.pos, 'feet': tuple([ (int(o[0]+self.pos[0]+a[0]), int(o[1]+self.pos[1]+a[1])) for o, a in orb_alf ]) }

Builder.load_string('''
<Foot>:
    id: 'foot'
    size: 50, 50
    size_hint: (None, None)
    canvas:
        Color:
            rgba: .1, .1, .4, 1.
        Ellipse:
            size: self.size
            pos: self.paso[0] - self.width/2, self.paso[1] - self.height/2

<Creature>:
    id: 'creature'
    size: 100, 100
    size_hint: (None, None)
    canvas:
        Color:
            rgba: .8, .6, 0, .5
        Ellipse:
            pos: self.pos
            size: self.size
            
<Muscle>:
    area: 300
    length: ((self.left_foot.center_x - self.right_foot.center_x)**2 + (self.left_foot.center_y - self.right_foot.center_y)**2)**0.5
    width: (self.area / (self.length + 0.001))
    canvas:
        Color:
            rgb: (.8, .4, .2)
        Line:
            width: self.width
            points: self.left_foot.center + self.right_foot.center

<Park>:
    canvas:
        Color:
            rgb: .02, .05, .0
        Rectangle:
            size: self.size
            pos: self.pos
''')

class Foot(Widget):
    paso = ListProperty([0., 0.])

class Muscle(Widget):
    left_foot = ObjectProperty(None)
    right_foot = ObjectProperty(None)
    def __init__(self, **kwargs):
        f1 = kwargs.pop('p1')
        f2 = kwargs.pop('p2')
        self.left_foot = f1
        self.right_foot = f2
        f1.bind(paso=self.set_left_foot)
        f2.bind(paso=self.set_right_foot)
        super().__init__(**kwargs)
    def set_right_foot(self, instance, value):
        self.right_foot.center = value
    def set_left_foot(self, instance, value):
        self.left_foot.center = value

class Anatomy(object):
    def __init__(self, feet=2, ligam_list=()):
        self.feet = feet
        from itertools import filterfalse
        self.ligam_list = tuple(filterfalse(lambda y:   not isinstance(y,(tuple, list)) or  \
                                                        len(y)!=2 or                        \
                                                        y[0] == y[1] or                     \
                                                        y[0] < 0 or y[0] >= feet or         \
                                                        y[1] < 0 or y[1] >= feet ,
                                            ligam_list))

class Creature(Widget):
    def __init__(self, **kwargs):
        anatomy = kwargs.pop('anatomy', Anatomy(feet=2, ligam_list=((0,1),)))
        self.movement = kwargs.pop('movement', Movement(radio=100, vel=200, amp=20, frec=10., box=Window))
        super().__init__(**kwargs)
        if not anatomy:
            from random import randint
            n = randint(1,5)
            self.movement.set_n(n*2)
            for _ in range(n):
                f1 = Foot()
                f2 = Foot()
                m = Muscle(p1=f1, p2=f2)
                self.add_widget(f1)
                self.add_widget(f2)
                self.add_widget(m)
        else:
            self.movement.set_n(anatomy.feet)
            feet_list = [ Foot() for _ in range(anatomy.feet) ]
            musc_list = [ Muscle(p1=feet_list[p[0]], p2=feet_list[p[1]]) for p in anatomy.ligam_list ]
            for foot in feet_list:
                self.add_widget(foot)
            for musc in musc_list:
                self.add_widget(musc)

    def move(self, dt):
        movenow = self.movement(dt)
        self.center = movenow['pos']
        feet = [ f for f in self.children if isinstance(f, Foot) ]
        for i, ch in enumerate(feet):
            ch.paso = movenow['feet'][i]
        # muscles = [ m for m in self.children if isinstance(m, Muscle) ]

class Park(FloatLayout):
    dt = 0.01
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_interval(self.move, self.dt)
    def on_size(self, instance, value):
        print('resizing')
        if Movement.box:
            Movement.box.width = value[0]
            Movement.box.height = value[1]
            print(Movement.box.width, Movement.box.height)
    def move(self, dt):
        Movement.inc_t(dt)
        for ch in self.children:
            ch.move(dt)

def rand_ligaments(n, prob):
    from random import random
    from itertools import filterfalse, chain
    return tuple(filterfalse(lambda x: random()>prob, chain( *(  [(i,j) for j in range(i)] for i in range(n) ) )))
from random import randint
prob, pies_random = 0.3, [ randint(2,8) for _ in range(10) ]
fauna = [ Anatomy(feet=r, ligam_list=rand_ligaments(r, prob)) for r in pies_random ]

class ParkApp(App):
    def build(self):
        b = Park()
        for f in fauna:
            b.add_widget(Creature(anatomy=f))
        return b

if __name__ == "__main__":
    ParkApp().run()
