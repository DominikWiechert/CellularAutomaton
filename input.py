import math
from typing import List

from matplotlib import pyplot as plt

from custom_datatypes import MapNode, LandUse
from pathlib import Path
import cv2
import numpy as np
from pykrige.ok import OrdinaryKriging

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
    input_image = cv2.cvtColor(input_image, cv2.COLOR_BGR2Luv)
    forest_color = get_forest_color_luv()
    [l_forest, u_forest, v_forest] = forest_color[0], forest_color[1], forest_color[2]

    # Example height datapoints
    # TODO: Input height datapoints
    data_heights_x = np.array([10, 20, grid_width-1, 80], dtype=float)
    data_heights_y = np.array([10, 60, grid_height-1, 75], dtype=float)
    data_heights = np.array([100, 50, 200, 20], dtype=float)

    # Grid for interpolation
    grid_x = np.arange(0, grid_width, 1, dtype=float)
    grid_y = np.arange(0, grid_height, 1, dtype=float)

    # Ordinary Kriging
    OK = OrdinaryKriging(
        data_heights_x,
        data_heights_y,
        data_heights,
        variogram_model='spherical',
        verbose=False,
        enable_plotting=False
    )

    # Interpolation
    interpolated_heights, ss = OK.execute('grid', grid_x, grid_y)

    show_height_graph = False
    if show_height_graph:
        plt.figure(figsize=(6, 5))
        plt.contourf(grid_x, grid_y, interpolated_heights, cmap='viridis')
        plt.scatter(data_heights_x, data_heights_y, c=data_heights, edgecolor='k', cmap='viridis')
        plt.colorbar(label='Interpolierte Höhe')
        plt.title("Ordinary Kriging – Interpolated Heights")
        plt.xlabel("x")
        plt.ylabel("y")
        plt.show()

    output_grid = []
    for i_height in range(input_image.shape[0]):
        row = []
        for i_width in range(input_image.shape[1]):
            pixel_height = interpolated_heights[i_height][i_width]
            l_pixel, u_pixel, v_pixel = input_image[i_height, i_width]
            d_pixel2forest = math.sqrt((int(l_pixel) - int(l_forest))**2 +
                                       (int(u_pixel) - int(u_forest))**2 +
                                       (int(v_pixel) - int(v_forest))**2)
            if d_pixel2forest < 40:
                row.append(MapNode(land_use=LandUse.FOREST, height=pixel_height))
            else:
                row.append(MapNode(land_use=LandUse.MISC, height=pixel_height))
        output_grid.append(row)
    return output_grid


def get_forest_color_luv() -> List[int]:
    forest_image_path = Path().cwd() / 'map_pictures' / 'only_forest.png'

    forest_image = cv2.imread(str(forest_image_path))
    forest_image = cv2.resize(forest_image, (1, 1))
    forest_image = cv2.cvtColor(forest_image, cv2.COLOR_BGR2Luv)

    l, u, v = forest_image[0, 0]
    return [l, u, v]


if __name__ == "__main__":
    # Just for debug purposes
    map_path = Path().cwd() / 'map_pictures' / 'osm_map.png'
    get_forest_map(map_path = map_path)