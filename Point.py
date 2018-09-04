class Point:
    def __init__(self, orientation, position, timestamp):
        self.orientation = orientation
        self.position = position
        self.timestamp = timestamp


class Orientation:
    def __init__(self, w, x, y, z):
        self.w = w
        self.x = x
        self.y = y
        self.z = z


class Position:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
