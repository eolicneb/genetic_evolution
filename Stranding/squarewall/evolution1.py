"""

In this version the creature controles its leading
direction and its advance, so that its response come
to be independant from the track's main direction
"""
import numpy as np
from kivy.app import App
import squarewall as sq
from thinking import Brain
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.graphics import *
from kivy.core.window import Window
from kivy.properties import ListProperty, ObjectProperty, NumericProperty, StringProperty
from random import random
from math import pi
from track import Track, directions, xy_from_polar
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.vector import Vector
from kivy.uix.recycleview.views import _cached_views, _view_base_cache

schema = (8, 10, 6, 4)
population = 20
top_most_show = 10
reproductions = population // 2 - population // 10 - 1
dt = 10.
iterations = 0
time_steps = 200
creature_size = 20
dad_color=(.1, .8, .0, .8) # Fathers are green
son_color=(.2, .0, .8, .8) # Sons are blue
new_color=(.8, .0, .7, .8) # Newcomers are pink
sq.Park.dt = dt
sq.Park.df = .03
Brain.mutation_factor = 0.01
visualize = True

track = Track(width=60, radius=180, center=Window.center, offset=(40, 0))
launch = track.initial_pos

class Eden(sq.Park):
    def new_era(self, deltat):
        # print(RegisteredMov.livings, len(self.children))
        # printzoo()
        # print(f'{RegisteredMov.livings:5d} creatures alive, only {len(self.children)-2} in Eden')
        RegisteredMov.inc_t(deltat)
        sq.Fauna.Darwin.sort(reverse=True, key=lambda x: x[0])
        if sq.Fauna.Darwin:
            for creat in sq.Fauna.Darwin[:top_most_show]:
                if creat[1] and not creat[1].parent:
                    sq.Fauna.root.add_widget(creat[1])
                
            for creat in sq.Fauna.Darwin[top_most_show:]:
                if creat[1] and creat[1].parent:
                    sq.Fauna.root.remove_widget(creat[1])
        sq.Fauna.Darwin = []

        # Evolving time
        if RegisteredMov.livings == 0 or RegisteredMov.t > time_steps*dt:
            # sq.Fauna.root.allow_move = False
            Clock.unschedule(super().move)
            print('It`s time to evolve again!')
            for ch in self.children:
                if isinstance(ch, sq.Creature):
                    print(f'{ch.name} in Eden {ch.parent}')
                    self.remove_widget(ch)
                else:
                    print(f'{ch} is not a Creature')
            print(f'{len(self.children)} creatures in Eden before evolving')
            for ch in self.children:
                if isinstance(ch, sq.Creature):
                    print(f'{ch.name} in Eden {ch.parent}')
                    self.remove_widget(ch)
                else:
                    print(f'{ch} is not a Creature')
            evolve()    
            print(f'{len(self.children)} creatures in Eden after evolving')
            for creature in sq.Fauna.zoo:
                if creature.parent:
                    print(f'{creature.name} already in {creature.parent}!!')
                    creature.parent.remove_widget(creature)
                self.add_widget(creature)
                creature.pos = launch[:]
                creature.mov.pos = launch[:]
            RegisteredMov.t = 0
            Clock.schedule_interval(super().move, self.df)
            # sq.Fauna.root.allow_move = True

    def on_touch_down(self, touch):
        self.allow_move = not self.allow_move
        if self.allow_move:
            Clock.schedule_interval(super().move, self.df)
        else:
            Clock.unschedule(super().move)
        print(f'Screen touched: {touch}')
        
class Discus(Widget):
    radius = NumericProperty(400)
    def __init__(self, **kwargs):
        radius = kwargs.pop('radius', 400)
        color = kwargs.pop('color', (.5, .5, .5, .5))
        super().__init__(**kwargs)
        self.pos = kwargs.pop('pos', (Window.width/2, Window.height/2))
        self.pos = Vector(*self.pos)-(radius, radius)
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
        self.size = (creature_size, creature_size)
    def move(self, dt):
        if not self.mov.alive and self.parent:
            self.parent.remove_widget(self)
            print(f'{self.name} died!')
        else:
            pos = self.mov(dt)
            if pos:
                self.pos = pos
                sq.Fauna.Darwin.append((self.mov.distance**2, self))
                self.move_whiskers()
                self.achieve = f'{self.mov.distance:6.2f} rad'
            else:
                if self.parent:
                    self.parent.remove_widget(self)
                # print(f'{self.name} terminated! Remaining creatures: {RegisteredMov.livings}')
    def move_whiskers(self):
        self.whisker.pos = Vector(*xy_from_polar(10., self.mov.nose)) + self.pos

class RegisteredMov(sq.Movement):
    loss_factor = np.array((1., .0))
    livings = 0
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        RegisteredMov.livings += 1
        self.register = ()
        self.alive = True
        self.nose = pi/2 # movement's leading direction
    def __call__(self, dt):
        if self.alive:
            # self.pos, self.old_pos = pos, tuple(pos)
            return self.perception(dt)
        return None
    def perception(self, dt):
        input_ = [ self.track.dist(self.pos, di_) \
                for di_ in directions(self.brain.schema[0], self.nose) ]
        if input_[0]:
            input_ = (np.array(input_)**(-1.)).clip(0,10)
            self.input_ = input_ # + self.old_pos
            # After the thinking input is build, the current
            # position is saved for the next movement step.
            self.old_pos = tuple(self.pos)
            return self.response(dt)
        self.final(kill=True)
        return None
    def response(self, dt):
        out_ = self.brain.think(self.input_)
        deltaNose, deltaPos = float(out_[0] - out_[1]), float(out_[2] - out_[3])
        self.nose += deltaNose*dt # Leading direction twisted
        # xy_from_polar needs a modulus and phase angle
        # but can also take a center parameter to shift
        # the returned vector, and thus the pos is updated
        self.pos = list(xy_from_polar(dt, self.nose, self.pos))
        self.statistics()
        return self.pos if self.alive else None
    def statistics(self):
        ang_var = self.track.ang_variation(self.pos, self.old_pos)
        # if self.distance != 0.0 and ang_var*self.distance <= 0:
        #     self.final(kill=True)
        self.distance += ang_var
        # print(f'Stranded angle so far: {self.distance}, variation: {ang_var}, current position: {self.pos}, previous position: {self.old_pos}')
    def final(self, kill=False):
        if self.alive:
            if kill or not self.track.is_in_track(self.pos):
                RegisteredMov.livings -= 1
                achive = (self.distance, self.t-self.t_inicial)
                self.t_inicial, self.distance = self.t, 0.0
                self.register = ((self.loss(achive),) + achive)
                self.alive = False
                return True
        return False
    def loss(self, achive):
        r = np.array(achive)
        return (self.loss_factor*(r*r)).sum() # reg[0]*reg[0]+reg[1]*reg[1]*self.time_factor*self.time_factor
    def reset(self):
        self.alive = True
        self.t_inicial = .0
        self.distance = .0

sq.Fauna.Darwin = []
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
park.add_widget(Discus(radius=track.in_radius, color=(.0, .0, .0), pos=Vector(Window.center)+track.offset.tolist()))
for c in sq.Fauna.zoo:
    park.add_widget(c)
    c.pos = launch[:]
    c.mov.pos = launch[:]

def printzoo():
    for ix, creature in enumerate(sq.Fauna.zoo):
        print(f'{ix:4d}: {creature.name} is{"" if creature.parent == sq.Fauna.root else " NOT"} in Eden in position {creature.pos}')

darwin=[]

def evolve():
    darwin = []
    for ix, c in enumerate(sq.Fauna.zoo):
        # if c.movable:

        c.mov.final(kill=True)
        print(c.name)
        darwin.append((c.mov.register, ix))
        print('  {:12.4f} d={:8.3f} t={:6.3f}'.format(*c.mov.register))
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
                size=(creature_size, creature_size),
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
        # root.remove_widget(sq.Fauna.zoo[cre])

        sq.Fauna.zoo[cre] = DiyingCreature(
                color=new_color,
                size=(creature_size, creature_size),
                movement=RegisteredMov(
                        pos=launch,
                        box=Window,
                        brain=Brain(schema=schema),
                        track=track
                        )
                )
        # print(f'{ix:4d}: {creature.name} is{"" if creature.parent == root else " NOT"} in Eden in position {creature.pos}')
    print(f'restaurando población. valor previo: {RegisteredMov.livings}')
    RegisteredMov.livings = population
    sq.Fauna.Darwin = []

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
        # f=FrameIt()
        # f.add_widget(park)
        return park

if visualize:
    ParkApp().run()