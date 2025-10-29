from enum import Enum

class LandUse(Enum):
    FOREST = 1
    STREET = 2

class NodeStatus(Enum):
    INTACT = 1
    BURNING = 2
    BURNT_DOWN = 3
    CANNOT_BURN = 4

class MapNode:
    def __init__(self, land_use: LandUse, height: float):
        self.land_use = land_use
        self.height = height
        self.status = NodeStatus.INTACT
        self.burning_duration = 0

class Probability:
    def __init__(self, base):
        self.base = base
        self.north = 0
        self.south = 0
        self.east = 0
        self.west = 0
