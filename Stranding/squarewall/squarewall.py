from kivy.app import App
from kivy.core.window import Window
from kivy.uix.floatlayout import FloatLayout
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty, NumericProperty, ListProperty, DictProperty

from thinking import Brain
import numpy as np


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

class Movement(object):
    box=None
    t = 0
    @classmethod
    def inc_t(cls, dt):
        cls.t += dt
    def __init__(self, box, pos, schema=(4,4), brain=None):
        self.box = box
        self.pos = pos
        if brain and isinstance(brain, Brain):
            self.brain = brain
        else:
            self.brain = Brain(schema=schema)
        self.distance = 0.0
        self.t_inicial = self.t
        self.fail_counter = 0
    def __call__(self, dt=1.):
        input_ = np.array((self.pos[0],
                            self.pos[1],
                            self.box.width - self.pos[0],
                            self.box.height - self.pos[1]
                            )).clip(0,10)
        out_ = self.brain.think(input_)
        # print('out: ', *out_)
        delta = (float(out_[0] - out_[1]), float(out_[2] - out_[3]))
        self.distance += (delta[0]*delta[0]*dt*dt + delta[1]*delta[1]*dt*dt)**.5
        self.pos[0] += delta[0]*dt
        self.pos[1] += delta[1]*dt
        margin = 50
        if self.pos[0] < margin:
            # print('{:8.4f} Falla {:4d}: distance={:8.5f}, time={:8.5f}'.format(self.t, *self.final()))
            self.final()
            self.pos[0] = self.box.width - margin
        if self.pos[1] < margin:
            # print('{:8.4f} Falla {:4d}: distance={:8.5f}, time={:8.5f}'.format(self.t, *self.final()))
            self.final()
            self.pos[1] = self.box.height - margin
        if self.pos[0] > self.box.width - margin:
            # print('{:8.4f} Falla {:4d}: distance={:8.5f}, time={:8.5f}'.format(self.t, *self.final()))
            self.final()
            self.pos[0] = margin
        if self.pos[1] > self.box.height - margin:
            # print('{:8.4f} Falla {:4d}: distance={:8.5f}, time={:8.5f}'.format(self.t, *self.final()))
            self.final()
            self.pos[1] = margin
        # print('pos: ', *self.pos)
        return self.pos
    def final(self):
        t, distance = self.t-self.t_inicial, self.distance
        self.t_inicial, self.distance = self.t, 0.0
        self.fail_counter += 1
        return self.fail_counter, distance, t

class Creature(Widget):
    counter = 0
    def __init__(self, **kwargs):
        schema = kwargs.pop('schema', (4,5,4))
        brain = kwargs.pop('brain', None)
        mov = kwargs.pop('movement', None)
        Creature.counter += 1
        self.name = kwargs.pop('name', 'creature{:03d}'.format(Creature.counter))
        super().__init__(**kwargs)
        self.mov = mov if mov else Movement(pos=self.pos, box=Window, schema=schema, brain=brain)
    def move(self, dt):
        self.pos = self.mov(dt)

class Park(FloatLayout):
    dt = 0.05
    df = 0.05
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_interval(self.move, self.df)
    def on_size(self, instance, value):
        print('resizing')
        if Movement.box:
            Movement.box.width = value[0]
            Movement.box.height = value[1]
            print(Movement.box.width, Movement.box.height)
    def move(self, dt):
        dt *= self.dt/self.df
        Movement.inc_t(dt)
        for ch in self.children:
            ch.move(dt)

class Fauna(object):
    zoo = []

class ParkApp(App):
    def build(self):
        b = Park()
        for c in Fauna.zoo:
            b.add_widget(c)
        return b

if __name__ == "__main__":
    Fauna.zoo = (Creature(brain=Brain(schema=(4,6,4))), Creature(brain=Brain(schema=(4,6,4))))
    ParkApp().run()
