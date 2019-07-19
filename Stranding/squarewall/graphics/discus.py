from kivy.properties import NumericProperty
from kivy.vector import Vector
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty
from kivy.graphics import *
        
class Discus(Widget):
    radius = NumericProperty(400)
    def __init__(self, **kwargs):
        radius = kwargs.pop('radius', 400)
        color = kwargs.pop('color', (.5, .5, .5, .1))
        super().__init__(**kwargs)
        self.pos = kwargs.pop('pos', (200, 200))
        self.pos = Vector(*self.pos)-(radius, radius)
        self.movable = False
        # self.center = (Window.width/2-radius, Window.height/2-radius)
        with self.canvas:
            Color(*color)
            Ellipse(pos=self.pos, size=(2*radius, 2*radius))

class CircusTrack(Discus):
    inner = ObjectProperty(None)
    def __init__(self, **kwargs):
        r_in = kwargs.pop('radius', 200)
        width = kwargs.pop('width', 50)
        centrum = kwargs.pop('center', (0, 0))
        offset = kwargs.pop('offset', (0, 0))
        kwargs.update({'radius': r_in+width,
                        'pos': centrum,
                        'color': (1, 1, 1, 1)})
        self.inner = Discus(pos=Vector(centrum)+offset,
                            radius=r_in, 
                            color=(0, 0, 0, 1))
        super().__init__(**kwargs)
        self.add_widget(self.inner)
        # with self.canvas.before:
        #     Color(0, 0, 0, 1)
        #     Ellipse(pos=Vector(centrum)-(r_in,r_in)+offset, size=(2*r_in,2*r_in))

if __name__ == '__main__':
    from kivy.app import App
    class TestApp(App):
        def build(self):
            pass