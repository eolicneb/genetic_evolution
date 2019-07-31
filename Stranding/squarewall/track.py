import numpy as np
# from kivy.uix.widget import Widget
# from kivy.properties import ObjectProperty
from kivy.vector import Vector

class CachedVal(object):
    """
    Serves as a cache for last evaluated value.
    If the point remains the same, the properties and evaluations
    that the path has stored in this cached copy will be returned
    without reevaluating.
    """
    def __init__(self, parent=None, cached={}, store={}):
        self.cached = cached
        self.store = store
    def __call__(self, other_value, func_repr):
        condition = np.array(other_value == self.cached.get(func_repr, None)).all()
        if condition:
            return True
        self.cached[func_repr] = other_value
        return False
    def ifNewVal(self, function):
        """ Decorator for cacheable functions
        """
        def check_cache(instance, new_val):
            func_name = repr(function)+repr(instance)
            # print(f'checking cached value for function {func_name}:')
            if not self.__call__(new_val, func_name):
                self.store[func_name] = function(instance, new_val)
                # print(f'\tWe\'ve got a new value {new_val}, it returns {self.store[func_name]}')
                return self.store[func_name]
            # print(f'\t{new_val} is cached, it returns {self.store[func_name]}')
            return self.store[func_name]
        return check_cache

cache = CachedVal().ifNewVal

def xy_from_polar(r, a, center=(0,0)):
    from math import sin, cos
    return (r*cos(a)+center[0], r*sin(a)+center[1])

def directions(N=4, Ph=0.):
    from math import pi
    return [xy_from_polar(1, a+Ph) for a \
            in ( i*2*pi/N for i in range(N) )]

def _det(m):
    # print(f'm = {m}')
    return m[0][0]*m[1][1] - m[0][1]*m[1][0]

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

def _existing_min(t1, t2):
    if not t2:
        return t1
    if not t1:
        return t2
    return min(t1, t2)

class _edge(object):
    def __init__(self, edge, left=None, right=None, next_=None):
        self.edge = (np.array(edge[0]), np.array(edge[1])) # ((0,0),(0,0))
        self.next_ = next_ # class <Tile>
        self.left = left # class <_edge>
        self.right = right # class <_edge>
    def intersect(self, point, dir_):
        point = np.array(point)
        d1, d2, E = np.array(dir_), self.edge[0]-self.edge[1], self.edge[0]-point
        det = _det((d1, d2))
        # print(f'det {det}')
        if det == 0:
            return None
        t, u = _det((E,d2))/det, _det((d1,E))/det
        if u < 0:
            return None # self.left.intersect(point, dir_)
        elif u > 1:
            return None # self.right.intersect(point, dir_)
        if t <= 0:
            return None
        if self.next_:
            point = point+d1*t*1.0000000001 # 
            # print(f'nexting.... point = {point}, dir = {d1}, t = {t}')
            dt = self.next_.intersect(point, dir_)
            return t + dt if dt else 0.0
        # print(f'returning distance {t}')
        return t
    def __getitem__(self, item):
        return self.edge[item]


class Tile(object):
    def __init__(self, **kwargs):
        self.points = kwargs.pop('points') # list of pairs (x, y)
        self.edges = self.build()
        self.box = self.build_box()
    def build(self):
        edges = []
        Lpoints = zip(self.points, list(self.points[1:])+[self.points[0]])
        for edge in Lpoints:
            edges.append(_edge(edge))
        for i, edge in enumerate(edges):
            edge.left, edge.right = edges[i-1], edges[(i+1)%len(edges)]
        return edges
    def build_box(self):
        px, py = zip(*self.points)
        return ((min(px), max(px)), (min(py), max(py)))
    def intersect(self, point, dir_):
        t=None
        for ix, edge in enumerate(self.edges):
            t = _existing_min(t, edge.intersect(point, dir_))
            # if t:
                # print(f't to break is {t} in edge {ix}')
        # print(f'Tile is returning a distance of {t}')
        return t
    @cache
    def inside(self, point):
        if not self.in_box(point):
            return 0.0
        if abs(self.cycling(point)) > 1:
            return True
        return False
    def cycling(self, point):
        from math import atan2
        angle, P = 0, Vector(point)
        for ed in self.edges:
            p1, p2 = -P+ed.edge[0], -P+ed.edge[1]
            angle += atan2(p2[1]*p1[0]-p2[0]*p1[1], 
                    p2[0]*p1[0]+p2[1]*p1[1])
            # print(f'partial angle {angle}, for p1 {p1} and p2 {p2}, y = {p2[0]*p1[0]+p2[1]*p1[1]:5.3f}, x = {p2[1]*p1[0]-p2[0]*p1[1]:5.3f}')
        return angle
    def in_box(self, point):
        if self.box[0][0] <= point[0] <= self.box[0][1] \
            and self.box[1][0] <= point[1] <= self.box[1][1]:
            return True
        return False
    def __str__(self):
        return 'Tile: ' + ', '.join(['({:5.3f}, {:5.3f})'.format(*z) for z in self.points])

class Path(object):
    def dist(self, point, dir_):
        if not self.is_in_track(point):
            return None
        dist, i = None, 0
        while i < len(self.tiles): # not dist and 
            dist = _existing_min(self.tiles[i].intersect(point, dir_), dist)
            i += 1
        # print(f'path returning distance {dist}')
        return dist
    @cache
    def is_in_track(self, point):
        # print('Just checking...')
        for tile in self.tiles:
            if tile.inside(point):
                return True
        return False
    def ang_variation(self, pos, old_pos):
        for tile in self.tiles:
            if tile.inside(old_pos):
                pos, old_pos = np.array(pos), np.array(old_pos)
                r = old_pos-self.center
                da = pos-old_pos
                r, da = (r*r).sum()**.5, (da*tile.dir).sum()
                return da/r
        return 0.0
    def __init__(self, **kwargs):
        self.contour = {
            'inner': kwargs.get('inner_points'),
            'outer': kwargs.get('outer_points')
        }
        self.initial_pos = (Vector(self.contour['inner'][0]) \
                            + self.contour['outer'][0]) / 2
        self.tiles = self.build()
        self.center = self.get_center(kwargs)
    def build(self):
        ins, ous = self.contour['inner'], self.contour['outer']
        tiles_points = zip(ous,ous[1:]+[ous[0]],ins[1:]+[ins[0]],ins)
        tiles = []
        for points in tiles_points:
            tiles.append(Tile(points=points))
        # now the path direction for each tile is setted
        for tile in tiles:
            d = np.array(tile.edges[2][0])-np.array(tile.edges[2][1])
            tile.dir = d/(d*d).sum()**.5
        for i in range(len(tiles)):
            tiles[i].edges[3].next_ = tiles[i-1]
            tiles[i-1].edges[1].next_ = tiles[i]
        return tiles
    def get_center(self, kwargs):
        center = kwargs.pop('center', None)
        if center:
            return np.array(center)
        contour = self.contour['outer']
        C = tuple(zip(*contour))
        return np.array(C).sum(0)/len(C)
 


if __name__ == "__main__":
    from math import pi, sin, cos
    import matplotlib.pyplot as plt

    def dires(N=4, R=1., d=0., center=(0, 0)):
        return [ (float(R*sin((2*pi*i+d)/N)+center[0]), float(R*cos((2*pi*i+d)/N)+center[1])) for i in range(N) ]

    print('Path class testing:')
    p = Path(inner_points=dires(8,1.0), outer_points=dires(8,2.0))
    for tile in p.tiles:
        px, py = zip(*tile.points)
        px, py = px+(px[0],), py+(py[0],)
        plt.plot(px,py,'y*-')
        print(f'{tile}:\n\tprev={tile.edges[3].next_}\n \
\tnext={tile.edges[1].next_}')

    for d in dires(N=6):
        print(f'{d}: {p.dist((0.01, -1.5), d)}')

    til = p.tiles[0]
    px, py = zip(*til.points)
    px, py = px+(px[0],), py+(py[0],)
    plt.plot(px,py,'y*-')
    print(px)
    print(py)
    test_points = ((-1.2, 0), (.4, 0.1), (.1, -1.5))
    colors = ('r', 'b', 'g')
    for cn, col in zip(test_points, colors):
        cn = np.array(cn)
        for d in dires(N=6):
            d = np.array(d)
            t = p.dist(cn, d)
            print(f'distance from {cn} in {d} direction = {t}')
            if t:
                q = cn + t*d
                plt.plot((cn[0], q[0]), (cn[1], q[1]), col+'o-')

    # cn = (.0001, 1.)
    # print(cn, p.tiles[0].cycling(cn))
    # plt.plot((cn[0],), (cn[1],), 'b*')
    # cn = (.7, 1.7)
    # print(cn, p.tiles[0].cycling(cn))
    # plt.plot((cn[0],), (cn[1],), 'g*')
    plt.show()
    
    # for d in dires():
    #     print(d)
    # corners = ((0,0), (1,0), (1,1), (0,1))
    # tile = Tile(points=corners)
    # print([e.edge for e in tile.edges])
    # for d in dires:
    #     print('intersection', d, tile.intersect((.5,.75), d))

    # edge = _edge(edge=((0,0), (0,1)))
    # print('edge:')
    # for d in dires:
    #     print('intersection', d, edge.intersect((.5,.5), d))
    
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
    