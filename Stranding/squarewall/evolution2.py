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
from graphics.discus import CircusTrack
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.vector import Vector
from kivy.uix.recycleview.views import _cached_views, _view_base_cache

schema = (12, 20, 10, 4)
population = 50
top_most_show = 10
reproductions = population // 2 - population // 10 - 1
dt = 10.
iterations = 0
time_steps = 200
creature_size = 20
dad_color=(.1, .8, .0, .8) # Fathers are green
son_color=(.2, .0, .8, .8) # Sons are blue
new_color=(.8, .0, .7, .8) # Newcomers are pink
df = .003
Brain.mutation_factor = 0.001
visualize = True
# 
track = Track(width=60, radius=180, center=Window.center, offset=(40, 0))
launch = track.initial_pos

class Eden(sq.Park):
    dt = dt
    df = df
    def move(self, dt):
        # print('Moving!')
        if self.allow_move:
            old_dt = dt
            dt *= self.dt/self.df
            # print(f'Times: given_dt={old_dt}, sim_dt={self.dt}, frame_dt={self.df}, actual_dt={dt}')
            dt = min((dt, self.dt)) # Limits the time step so nothing blows if dt is too large
            RegisteredMov.inc_t(dt)
            self.watch.text = f'time: {RegisteredMov.t:10.2f} s\nEpoch {sq.Fauna.epoch}\n{sq.Fauna.current_creature+1}: {sq.Fauna.zoo[sq.Fauna.current_creature].name}'
            ch = sq.Fauna.zoo[sq.Fauna.current_creature]
            if ch.mov.alive:
                ch.move(dt) 
            self.new_era()
    def new_era(self):
        # Evolving time
        if sq.Fauna.isEvolvingTime(sq.Fauna):
            Clock.unschedule(super().move)
            print('It`s time to evolve again!')
            evolve()
            RegisteredMov.t = 0
            Clock.schedule_interval(super().move, self.df)

    def on_touch_down(self, touch):
        print(f'Screen touched: {touch}')
        x, y = touch.spos[0], touch.spos[1]
        if .3 < x < .7:
            if .3 < y < .7:
                self.toggle_pause()
            elif y <= .3:
                self.df *= 2
                print(f'Frame time: {self.df} s')
            elif y >= .7:
                self.df /= 2
                print(f'Frame time: {self.df} s')
        elif .3 >= x:
            # dt /= 2
            self.dt /= 2
            print(f'Step time: {self.dt} s')
        elif x >= .7:
            # dt *= 2
            self.dt *= 2
            print(f'Step time: {self.dt} s')
    def toggle_pause(self):
        self.allow_move = not self.allow_move
        if self.allow_move:
            Clock.schedule_interval(super().move, self.df)
        else:
            Clock.unschedule(super().move)
        
# class Discus(Widget):
#     radius = NumericProperty(400)
#     def __init__(self, **kwargs):
#         radius = kwargs.pop('radius', 400)
#         color = kwargs.pop('color', (.5, .5, .5, .5))
#         super().__init__(**kwargs)
#         self.pos = kwargs.pop('pos', (Window.width/2, Window.height/2))
#         self.pos = Vector(*self.pos)-(radius, radius)
#         self.movable = False
#         # self.center = (Window.width/2-radius, Window.height/2-radius)
#         with self.canvas:
#             Color(*color)
#             Ellipse(pos=self.pos, size=(2*radius, 2*radius))

class DiyingCreature(sq.Creature):
    achieve = StringProperty('0.0 u')
    def __init__(self, **kwargs):
        self.achieve = '0.0 u'
        super().__init__(**kwargs)
        self.size = (creature_size, creature_size)
    def move(self, dt):
        if self.mov.alive:
            pos = self.mov(dt)
            if pos:
                self.pos = pos
                sq.Fauna.Darwin.append((self.mov.distance**2, self))
                self.move_whiskers()
                self.achieve = f'{self.mov.distance:6.2f} rad'
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
            # After the thinking input is built, the current
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

def isEvolvingTime(self):
    curcreat = self.zoo[self.current_creature]
    if RegisteredMov.t > time_steps*dt \
            or not curcreat.mov.alive:
        curcreat.parent.remove_widget(curcreat)
        if self.current_creature + 1 == len(self.zoo):
            self.current_creature = 0
            self.epoch += 1
            print(f'Epoch {self.epoch}')
            return True
        else:
            RegisteredMov.t = 0
            self.current_creature += 1
            curcreat = self.zoo[self.current_creature]
            self.root.add_widget(curcreat)
            curcreat.pos = launch[:]
            curcreat.mov.pos = launch[:]
    return  False
sq.Fauna.isEvolvingTime = isEvolvingTime

sq.Fauna.Darwin = []
sq.Fauna.epoch = 0
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
sq.Fauna.current_creature = 0

park = Eden()
t_pos = Vector(track.center.tolist())-(track.out_radius, track.out_radius)
print(t_pos)
circus = CircusTrack(radius=track.in_radius,
                            width=track.width,
                            pos=t_pos,
                            offset=track.offset.tolist())
park.add_widget(circus)
# park.add_widget(Discus(radius=track.out_radius, color=(1., 1., 1.)))
# park.add_widget(Discus(radius=track.in_radius, color=(.0, .0, .0), pos=Vector(Window.center)+track.offset.tolist()))
print('circus.center y .pos', circus.center, circus.pos)
print(circus.inner.center)
c = sq.Fauna.zoo[0]
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
    sq.Fauna.root.add_widget(sq.Fauna.zoo[sq.Fauna.current_creature])

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