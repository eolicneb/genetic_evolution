from kivy.app import App

from kivy.uix.label import Label

class FirstKivy(App):
    def build(self):
        return Label(text="Hello Kivy!")

# FirstKivy().run()

from kivy.uix.button import Button
from functools import partial

class SecondKivy(App):
    def disable(self, instance, *args):
        instance.disabled = True
    def update(self, instance, *args):
        instance.text = "I am Disabled!"
    def build(self):
        mybtn = Button(text="Click me to disable",
                       pos=(300,350), size_hint=(.25, .18),
                       background_color=(55,0,55,53))
        mybtn.bind(on_press=partial(self.disable, mybtn))
        mybtn.bind(on_press=partial(self.update, mybtn))
        return mybtn

# SecondKivy().run()

from kivy.lang import Builder

from kivy.uix.boxlayout import BoxLayout

Builder.load_file("myfile.kv")
class KivyButton(App, BoxLayout):
    def build(self):
        return self

# KivyButton().run()

from kivy.uix.recycleview import RecycleView

Builder.load_string("""
<ExampleRV>:
    viewclass: 'Button'
    RecycleBoxLayout:
        size_hint_y: None
        height: self.minimum_height
        orientation: 'vertical'
""")
class ExampleRV(RecycleView):
    def __init__(self, **kwargs):
        super(ExampleRV, self).__init__(**kwargs)
        self.data = [{'text': str(x)} for x in range(20)]
class RecycleApp(App):
    def build(self):
        return ExampleRV()
# RecycleApp().run()

from kivy.base import runTouchApp

root = Builder.load_string("""
ScrollView:
    Label:
        text: 'Scrollview Example ' * 100
        font_size: 30
        size_hint_x: 1.0
        size_hint_y: None
        text_size: self.width, None
        height: self.texture_size[1]
""")
# runTouchApp(root)

from kivy.uix.textinput import TextInput 

class ClearApp(App):
    def build(self):
        self.box = BoxLayout(orientation='horizontal', spacing=20, pos=(0, 550))
        self.txt = TextInput(hint_text='Write here', size_hint=(.5, .1))
        self.btn = Button(text='Clear All', on_press=self.clearText, size_hint=(.1, .1))
        self.box.add_widget(self.txt)
        self.box.add_widget(self.btn)
        return self.box
    def clearText(self, instance):
        self.txt.text = ''
# ClearApp().run()

from kivy.clock import Clock
class ClockExample(App):
    i = 0
    def build(self):
        self.mybtn = Button(text='Number of Calls')
        Clock.schedule_interval(self.Clock_Callback, 2)
        return self.mybtn
    def Clock_Callback(self, dt):
        self.i += 1
        self.mybtn.text = "Call = {:d}".format(self.i)
# ClockExample().run()

kvWidget = """
MyWidget:
    orientation: 'vertical'
    canvas:
        Rectangle:
            size: self.size
            pos: self.pos
            source: 'images.jpg'
"""
class MyWidget(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
class CanvasApp(App):
    def build(self):
        return Builder.load_string(kvWidget)
# CanvasApp().run()

from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty

class Pasos():
    def __init__(self, dt=1.0, f=1.0, A=1.0):
        self.t = 0.0
        self.dt = dt
        self.f = f
        self.A = A
    def __call__(self):
        from math import sin, cos
        a, A = self.t*self.f, self.A
        self.t += self.dt
        return ((A*sin(a), A*sin(a)), (-A*cos(a), A*cos(a)))

paseo = Pasos(A=10.0)

class Foot(Widget):
    def move(self, step):
        self.x += step[0]
        self.y += step[1]
class Body(Widget):
    pass
class Creature(Widget):
    trunk = ObjectProperty(None)
    lFoot = ObjectProperty(None)
    rFoot = ObjectProperty(None)
    def move(self):
        self.x += 1.0
        pasos = paseo()
        self.lFoot.move(pasos[0])
        self.rFoot.move(pasos[1])
class Park(BoxLayout):
    bicho = ObjectProperty(None)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_interval(self.update, 0.002)
    def update(self, dt):
        self.bicho.move()
class RunField(App):
    def build(self):
        return Builder.load_file('creature.kv')
RunField().run()
