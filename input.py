from typing import List
from custom_datatypes import MapNode, LandUse
from pathlib import Path

def get_forest_map(map_path: Path = None, stepsize: int = -1, grid_width: int = 10, grid_height: int = 10) -> List[List[MapNode]]:
    # TODO: Remove stub and insert implementation
    map_node = MapNode(land_use=LandUse.FOREST, height=0)
    map_row = [map_node for _ in range(grid_width)]
    stub_forest_map = [map_row for _ in range(grid_height)]
    return stub_forest_map


if __name__ == "__main__":
    get_forest_map()