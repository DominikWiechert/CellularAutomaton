from typing import List
from custom_datatypes import MapNode, LandUse
from pathlib import Path
import cv2


def get_forest_map(map_path: Path = None, max_axis_length: int = 200) -> List[List[MapNode]]:
    """
    Return a 2D forest map of a given map picture.
    :param map_path:
    :param max_axis_length:
    :return: 2D array
        forest_map[x][y]
               x (width)
           [0,0]--------->
           |
           |
           V
       y (height)
    """
    #
    input_image = cv2.imread(str(map_path))

    # Downscale image, maintain ratios
    size = input_image.shape
    ratio = size[1] / size[0]
    if size[1] > size[0]:
        grid_width = max_axis_length
        grid_height = int(grid_width / ratio)
    else:
        grid_height = max_axis_length
        grid_width = int(ratio * grid_height)
    input_image = cv2.resize(input_image,(grid_width, grid_height))

    # Read RGB and separate into terrain types. Generate grid
    grid = []
    for i_height in range(input_image.shape[0]):
        row = []
        for i_width in range(input_image.shape[1]):
            r, g, b = input_image[i_height, i_width]
            # TODO: Differentiate between different green tones. (e.g. light green is just a field, dark green is a forest). Might use a different colour representation (e.g. HSL)
            if g > r + 30 and g > b + 10:
                row.append(MapNode(land_use=LandUse.FOREST, height=0))
            else:
                row.append(MapNode(land_use=LandUse.MISC, height=0))
        grid.append(row)

    return grid


if __name__ == "__main__":
    # Just for debug purposes
    map_path = Path().cwd() / 'map_pictures' / 'osm_map.png'
    get_forest_map(map_path = map_path)