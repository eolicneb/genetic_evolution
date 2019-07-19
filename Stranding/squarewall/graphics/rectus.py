from kivy.properties import NumericProperty, ObjectProperty, ListProperty
from kivy.vector import Vector
from kivy.uix.widget import Widget
from kivy.graphics import *

class Rectus(Widget):
    width = NumericProperty(300)
    height = NumericProperty(200)
    size = ListProperty([width, height])
    def __init__(self, **kwargs):
        self.width = kwargs.pop('width', 300)
        self.height = kwargs.pop('height', 200)
        self.size = kwargs.get('size', ([self.width, self.height]))
        self.curve = kwargs.pop('curve', 0)
        self.color = kwargs.pop('color', (.5, .5, .5, .5))
        super().__init__(**kwargs)
        with self.canvas:
            Color(self.color)
            Line(rounded_rectangle=(self.pos[0],
                                    self.pos[1],
                                    self.size[0],
                                    self.size[1],
                                    self.curve))

class RectTrack(Rectus):
    def __init__(self, **kwargs):
        self.width = kwargs.pop('width', 50)
        quargs = kwargs.copy()
        pos = quargs.get('pos', (0,0))
        size = quargs.get('size', (300,200))
        quargs['pos'] = Vector(pos)+(self.width,self.width)
        quargs['size'] = Vector(size)-(2*self.width,2*self.width)
        quargs['curve'] -= self.width if quargs['curve'] > self.width else quargs['curve']
        self.rectus = Rectus(**quargs)
        super().__init__(**kwargs)
        self.add_widget(self.rectus)

if __name__ == '__main__':
    from kivy.base import runTouchApp
    from kivy.core.window import Window
    from kivy.vector import Vector

    r = RectTrack(curve=50, width=20, pos=Vector(Window.center)-(300/2, 200/2))
    runTouchApp(r)
