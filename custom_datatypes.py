from enum import Enum

class LandUse(Enum):
    FOREST = 1
    MISC = 2

class NodeStatus(Enum):
    INTACT = 1
    CROWN_BURNING = 2
    BURNT_DOWN = 3
    CANNOT_BURN = 4
    LOWER_BURNING = 5

class MapNode:
    def __init__(self, land_use: LandUse, height: float):
        self.land_use = land_use
        if self.land_use == LandUse.FOREST:
            self.status = NodeStatus.INTACT
        else:
            self.status = NodeStatus.CANNOT_BURN
        self.height = height
        self.burning_duration = 0

class Probability:
    def __init__(self, base):
        self.base = base
        self.north = 0
        self.south = 0
        self.east = 0
        self.west = 0

class OptimisedCell:
    def __init__(self, color: str, x: int, y: int, old_color: str):
        self.color = color
        self.x = x
        self.y = y
        self.old_color = old_color