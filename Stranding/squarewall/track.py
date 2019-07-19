import numpy as np
# from kivy.uix.widget import Widget
# from kivy.properties import ObjectProperty
from kivy.vector import Vector

def xy_from_polar(r, a, center=(0,0)):
    from math import sin, cos
    return (r*cos(a)+center[0], r*sin(a)+center[1])

def directions(N=4, Ph=0.):
    from math import pi
    return [xy_from_polar(1, a+Ph) for a \
            in ( i*2*pi/N for i in range(N) )]

def _intersect(rad, cen, pos, di_):
    pos, di_ = np.array(pos) - cen, np.array(di_)
    cent = (pos*di_).sum()/(di_*di_).sum()
    disc = (cent)**2 - ((pos*pos).sum()-rad**2)/(di_*di_).sum()
    # print(cent, disc)
    if disc >= 0:
        t1, t2 = -cent + disc**.5, -cent - disc**.5
        # print(t1, t2)
        if t2 >= 0:
            return (di_*di_).sum()**.5*t2
        elif t1 >= 0:
            return (di_*di_).sum()**.5*t1
    return None

def _inside(rad, cen, pos):
    dis = np.array(pos) - cen
    dis = (dis*dis).sum()**.5
    return  dis < rad

class Track(object):
    def __init__(self, width=50, **kwargs):
        self.width = width
        self.build_track(**kwargs)
        self.build_widget()
    def build_track(self, **kwargs):
        center = kwargs.get('center', (0, 0))
        self.in_radius = kwargs.get('radius', 300)
        self.offset = np.array(kwargs.get('offset', (0, 0)))
        self.initial_pos = [center[0] - self.in_radius - self.width/2, center[1]]
        self.center = np.array(center)
        self.out_radius = self.in_radius + self.width
        # self.initial_pos = [self.center[0] - self.in_radius - self.width/2, self.center[1]]
    def is_in_track(self, pos):
        return _inside(self.out_radius, self.center, pos) \
                and not _inside(self.in_radius, self.center+self.offset, pos)
    def dist(self, pos, di_):
        if self.is_in_track(pos):
            inte1 = _intersect(self.in_radius, self.center+self.offset, pos, di_)
            inte2 = _intersect(self.out_radius, self.center, pos, di_)
            if inte1 == None:
                if inte2 == None:
                    return None
                else:
                    return inte2
            else:
                if inte2 == None:
                    return inte1
                else:
                    return min((inte1, inte2))
        return None
    def ang_variation(self, pos, old_pos):
        p = np.array(pos)
        r = p-self.center # Vector from the center of the track to current position 
        t = np.array((-r[1], r[0])) # Normal to r vector
        R = (r*r).sum()**.5 # r and t modulus
        # print(f'p1: {pos}, p2: {old_pos}, r: {r}, t: {t}, R: {R}')
        return ((p-np.array(old_pos))*t).sum()/R/R  
    def build_widget(self):
        pass
    def track_widget(self):
        pass

class _edge(object):
    def __init__(self, edge, left=None, right=None, next_=None):
        self.edge = edge # ((0,0),(0,0))
        self.next_ = next_ # class <Tile>
        self.left = left # class <_edge>
        self.right = right # class <_edge>
    def intersect(self, point, dir_):
        if self.next_:
            return self.next_.intersect(point, dir_)
        e1, e2 = self.edge
        P, E, V = point, (e2[0]-e1[0],e2[1]-e1[1]), dir_
        print('P:', P)
        print('E:', E)
        print('V:', V)
        D = Vector(e1)-P
        det = (V[0]*E[1] - V[1]*E[0])
        if det == 0:
            return None
        u = -((D[0])*V[1] - (D[1]*V[0]))/det
        if u < 0:
            return None # self.left.intersect(point, dir_)
        elif u > 1:
            return None # self.right.intersect(point, dir_)
        t = ((D[0])*E[1] - (D[1]*E[0]))/det
        if t < 0:
            return None
        return t


class Tile(object):
    def __init__(self, **kwargs):
        self.points = kwargs.pop('points') # list of pairs (x, y)
        self.edges = self.build()
    def build(self):
        edges = []
        Lpoints = zip(self.points, list(self.points[1:])+[self.points[0]])
        for edge in Lpoints:
            edges.append(_edge(edge))
        for i, edge in enumerate(edges):
            edge.left, edge.right = edges[i-1], edges[(i+1)%len(edges)]
        return edges
    def intersect(self, point, dir_):
        for edge in self.edges:
            t = edge.intersect(point, dir_)
            if t:
                break
            return t

if __name__ == "__main__":
    from math import pi, sin, cos
    # center = (30, 0)
    # track = Track(width=10, radius=100, center=center)
    # N = 8
    # for di_ in directions(N):
    #     a = 2*2*pi/N
    #     pos = xy_from_polar(100, a, (0, 0)) 
    #     # di_ = xy_from_polar(80, a+pi) 
    #     print(f'pos: {pos}, direction: {di_}')
    #     print('distance: ', track.dist(pos, di_))
    # print(f'ang ', track.ang_variation(xy_from_polar(5, 2.8, center),xy_from_polar(4, 2.5, center)))
    N = 8
    dires = [ (float(sin(pi*i/N)), float(cos(pi*i/N))) for i in range(N) ]
    for d in dires:
        print(d)
    corners = ((0,0), (1,0), (1,1), (0,1))
    tile = Tile(points=corners)
    print([e.edge for e in tile.edges])
    for d in dires:
        print('intersection', d, tile.intersect((.5,.5), d))