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