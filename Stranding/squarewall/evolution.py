import numpy as np
from kivy.app import App
import squarewall as sq
from thinking import Brain
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.graphics import *
from kivy.core.window import Window
from kivy.properties import ListProperty, ObjectProperty, NumericProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from random import random
from track import Track, directions
from kivy.clock import Clock
from kivy.lang import Builder

schema = (8, 10, 6, 4)
population = 200
reproductions = population // 3
dt = .01
iterations = 0
time_steps = 2000
creature_size = 20
dad_color=(.1, .8, .0, .8) # Fathers are green
son_color=(.2, .0, .8, .8) # Sons are blue
new_color=(.8, .0, .7, .8) # Newcomers are pink
sq.Park.dt = dt
sq.Park.df = .01
Brain.mutation_factor = 0.0001
visualize = True

track = Track(width=70, radius=180, center=Window.center)
launch = track.initial_pos

class Eden(sq.Park):
    def new_era(self, deltat):
        # print(RegisteredMov.livings, len(self.children))
        # printzoo()
        # print(f'{RegisteredMov.livings:5d} creatures alive, only {len(self.children)-2} in Eden')
        RegisteredMov.inc_t(deltat)
        if RegisteredMov.livings == 0 or RegisteredMov.t > time_steps*dt:
            print('It`s time to evolve again!')
            evolve()
            RegisteredMov.t = 0
        
class Discus(Widget):
    radius = NumericProperty(400)
    def __init__(self, **kwargs):
        radius = kwargs.pop('radius', 400)
        color = kwargs.pop('color', (.5, .5, .5, .5))
        super().__init__(**kwargs)
        self.pos = kwargs.pop('pos', (Window.width/2-radius, Window.height/2-radius))
        self.movable = False
        # self.center = (Window.width/2-radius, Window.height/2-radius)
        with self.canvas:
            Color(*color)
            Ellipse(pos=self.pos, size=(2*radius, 2*radius))

class DiyingCreature(sq.Creature):
    achieve = StringProperty('0.0 u')
    def __init__(self, **kwargs):
        self.achieve = '0.0 u'
        super().__init__(**kwargs)
    def move(self, dt):
        if not self.mov.alive and self.parent:
            self.parent.remove_widget(self)
        else:
            pos = self.mov(self.pos, dt)
            if pos:
                self.pos = pos
                self.achieve = f'{self.mov.distance:6.2f} rad'
            else:
                self.parent.remove_widget(self)
                # print(f'{self.name} terminated! Remaining creatures: {RegisteredMov.livings}')

class RegisteredMov(sq.Movement):
    loss_factor = np.array((1., .0, 8.))
    livings = 0
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        RegisteredMov.livings += 1
        self.register = ()
        self.alive = True
    def __call__(self, pos, dt):
        if self.alive:
            self.pos, self.old_pos = pos, tuple(pos)
            return self.perception(dt)
        return None
    def perception(self, dt):
        input_ = [ self.track.dist(self.pos, di_) \
                for di_ in directions(self.brain.schema[0]) ]
        if input_[0]:
            input_ = np.array(input_) # .clip(0,10)
            self.input_ = input_
            return self.response(dt)
        self.final(kill=True)
        return None
    def response(self, dt):
        out_ = self.brain.think(self.input_)
        delta = (float(out_[0] - out_[1]), float(out_[2] - out_[3]))
        self.pos[0] += delta[0]*dt
        self.pos[1] += delta[1]*dt
        self.statistics()
        return self.pos if self.alive else None
    def statistics(self):
        ang_var = self.track.ang_variation(self.pos, self.old_pos)
        if self.distance != 0.0 and ang_var*self.distance <= 0:
            self.final(kill=True)
        self.distance += ang_var
        # print(f'Stranded angle so far: {self.distance}, variation: {ang_var}, current position: {self.pos}, previous position: {self.old_pos}')
    def final(self, kill=False):
        if self.alive:
            if kill or not self.track.is_in_track(self.pos):
                RegisteredMov.livings -= 1
                achive = (self.distance, self.t-self.t_inicial, 0) #min(self.input_))
                self.t_inicial, self.distance = self.t, 0.0
                self.fail_counter += 1
                self.register = ((self.loss(achive), self.fail_counter) + achive)
                self.alive = False
                return True
        return False
    def loss(self, reg):
        r = np.array(reg)
        return (self.loss_factor*(r*r)).sum() # reg[0]*reg[0]+reg[1]*reg[1]*self.time_factor*self.time_factor
    def reset(self):
        self.alive = True

sq.Fauna.genes = [ Brain(schema=schema) for _ in range(population) ]
sq.Fauna.zoo = [ DiyingCreature(
                        color=new_color,
                        size=(20, 20),
                        movement=RegisteredMov(
                                                pos=launch, 
                                                box=Window, 
                                                brain=b,
                                                track=track)
                        ) for b in sq.Fauna.genes ]

park = Eden()
park.add_widget(Discus(radius=track.out_radius, color=(1., 1., 1.)))
park.add_widget(Discus(radius=track.in_radius, color=(.0, .0, .0)))
for c in sq.Fauna.zoo:
    park.add_widget(c)
    c.pos = launch
    c.mov.pos = launch

def printzoo():
    for ix, creature in enumerate(sq.Fauna.zoo):
        print(f'{ix:4d}: {creature.name} is{"" if creature.parent == sq.Fauna.root else " NOT"} in Eden in position {creature.pos}')

darwin=[]

def evolve():
    sq.Fauna.root.allow_move = False
    darwin = []
    for ix, c in enumerate(sq.Fauna.zoo):
        # if c.movable:

        c.mov.final(kill=True)
        print(c.name)
        darwin.append((c.mov.register, ix))
        print('  {:12.4f} {:4d} d={:8.3f} t={:6.3f} separation={:6.3f}'.format(*c.mov.register))
    darwin.sort(reverse=True)
    data = [ reg[0][0] for reg in darwin ]
    print(f'| | | | Max loss = {data[0]} for {sq.Fauna.zoo[darwin[0][1]].name}, average = {np.average(data)}')

    # Reproduction time!
    R, P, root = reproductions, population, sq.Fauna.root
    for dad, son in zip(darwin[:R], darwin[R:2*R]):
        # dad, son = dad[1], son[1]
        print(f'dad {sq.Fauna.zoo[dad[1]].name}, son {sq.Fauna.zoo[son[1]].name}')
        sq.Fauna.zoo[dad[1]].color = dad_color
        sq.Fauna.zoo[son[1]] = DiyingCreature(
                size=(20, 20),
                color=son_color,
                movement=RegisteredMov(
                        pos=launch, 
                        box=Window, 
                        brain=Brain(
                                schema=schema,
                                layers=sq.Fauna.zoo[dad[1]].mov.brain.layers
                                ),
                        track=track
                        )
                )
        sq.Fauna.zoo[son[1]].mov.brain.mutate()
        sq.Fauna.zoo[dad[1]].mov.reset()
    
    for cre in darwin[2*R:P]:
        cre = cre[1]
        # First, remove dead creatures from root widget
        root.remove_widget(sq.Fauna.zoo[cre])

        sq.Fauna.zoo[cre] = DiyingCreature(
                color=new_color,
                size=(20, 20),
                movement=RegisteredMov(
                        pos=launch,
                        box=Window,
                        brain=Brain(schema=schema),
                        track=track
                        )
                )
    
    for ix, creature in enumerate(sq.Fauna.zoo):
        if not creature.parent:
            root.add_widget(creature)
        creature.pos = launch
        creature.mov.pos = launch
        # print(f'{ix:4d}: {creature.name} is{"" if creature.parent == root else " NOT"} in Eden in position {creature.pos}')
    print(f'restaurando población. valor previo: {RegisteredMov.livings}')
    RegisteredMov.livings = population
    sq.Fauna.root.allow_move = True

def new_epoch():
    print('Iteration ', iteration)

    for _ in range(time_steps):
        RegisteredMov.inc_t(dt)
        pop = 0
        for c in sq.Fauna.zoo:
            if c.mov.alive:
                c.move(dt)
                pop +=1
        if not pop:
            break
        # print(f't={RegisteredMov.t} {pop} folks')
    evolve()


for iteration in range(iterations):
    new_epoch()


class ParkApp(App):
    def build(self):
        f=FrameIt()
        # f.add_widget(park)
        return park

if visualize:
    ParkApp().run()