from kivy.app import App
from kivy.core.window import Window
from kivy.uix.floatlayout import FloatLayout
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty, StringProperty, NumericProperty, ListProperty, DictProperty

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

<Whisker>:
    size_hint: (None, None)
    color: (.9, .9, .0, 1.)
    width: 2
    canvas:
        Color:
            rgba: self.color
        Line:
            points: self.parent.pos + self.pos
            width: self.width

<Creature>:
    id: 'creature'
    size: 100, 100
    size_hint: (None, None)
    color: (.8, .6, .0, .5)
    whisker: whisker
    # achieve: ''
    # pos: (0., 0.)
    # name: 'a'
    canvas:
        Color:
            rgba: self.color
        Ellipse:
            pos: (self.pos[0] - self.size[0]/2, self.pos[1] - self.size[1]/2)
            size: self.size
    Whisker:
        id: whisker
        pos: self.parent.center
    Label:
        id: ticket
        # pos_hint: {'y': 2, 'x': 1}
        pos: (self.parent.pos[0], self.parent.pos[1] + self.parent.size[1]/2)
        text: self.parent.name + '\' + self.parent.achieve
        size: self.texture_size
        color: self.parent.color
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
class Whisker(Widget):
    whisker = ObjectProperty(None)

class Movement(object):
    box=None
    t = 0
    @classmethod
    def inc_t(cls, dt):
        cls.t += dt
    def __init__(self, box=(100,100), pos=(0,0), schema=(4,4), brain=None, track=None):
        self.box = box
        self.pos = pos
        if brain and isinstance(brain, Brain):
            self.brain = brain
        else:
            self.brain = Brain(schema=schema)
        self.distance = 0.0
        self.t_inicial = self.t
        self.fail_counter = 0
        self.track = track
    def __call__(self, dt=1.):
        if self.track:
            # self.perception()
            # self.response()
            return self.pos
        else:
            input_ = np.array((self.pos[0],
                                self.pos[1],
                                self.box.width - self.pos[0],
                                self.box.height - self.pos[1]
                                )).clip(0,100)
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
    color = ListProperty((.8, .6, .0, .5))
    movable = True
    def __init__(self, **kwargs):
        schema = kwargs.pop('schema', (4,5,4))
        brain = kwargs.pop('brain', None)
        mov = kwargs.pop('movement', None)
        Creature.counter += 1
        self.name = kwargs.pop('name', 'creature{:03d}'.format(Creature.counter))
        color = kwargs.pop('color', None)
        super().__init__(**kwargs)
        if color:
            self.color = color
        self.mov = mov if mov else Movement(pos=self.pos, box=Window, schema=schema, brain=brain)
    def move(self, dt):
        self.pos = self.mov(dt)

class Park(FloatLayout):
    dt = 0.1
    df = 0.05
    allow_move = True
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_interval(self.move, self.df)
        Fauna.root = self
    def on_size(self, instance, value):
        print('resizing')
        if Movement.box:
            Movement.box.width = value[0]
            Movement.box.height = value[1]
            print(Movement.box.width, Movement.box.height)
    def move(self, dt):
        print('Moving!')
        if self.allow_move:
            old_dt = dt
            dt *= self.dt/self.df
            # print(f'Times: given_dt={old_dt}, sim_dt={self.dt}, frame_dt={self.df}, actual_dt={dt}')
            dt = min((dt, self.dt)) # Limits the time step so nothing blows if dt is too large
            Movement.inc_t(dt)
            for ch in Fauna.zoo:
                if ch.mov.alive:
                    ch.move(dt) 
            self.new_era(dt)
    def new_era(self, dt):
        print('new era')

class Fauna(object):
    # root = Widget()
    zoo = []

class ParkApp(App):
    park = None
    def build(self):
        self.park = Park()
        for c in Fauna.zoo:
            self.park.add_widget(c)
        return self.park

if __name__ == "__main__":
    Fauna.zoo = (Creature(color=(.2, .8, .1, .5), brain=Brain(schema=(4,6,4))), Creature(brain=Brain(schema=(4,6,4))))
    Fauna.zoo[1].color = (.2, .8, .9, .5)
    ParkApp().run()
