from kivy.properties import NumericProperty, ObjectProperty, ListProperty
from kivy.vector import Vector
from kivy.uix.widget import Widget
from kivy.graphics import *

class PolyTrack(Widget):
    line_width = NumericProperty(4.0)
    def __init__(self, **kwargs):
        self.line_width = kwargs.pop('width', 4.0)
        poly = kwargs.pop('points', ((0, 0)))
        self.poly = []
        for point in poly:
            print(point)
            self.poly.extend(point)
        self.poly.extend(poly[0])
        super().__init__(**kwargs)
        with self.canvas:
            Line(points=self.poly)

if __name__ == '__main__':
    points = [
                (0, 0),
                (100, 50),
                (50, 100)
            ]
    poly = PolyTrack(points=points)
    from kivy.base import runTouchApp
    runTouchApp(poly)