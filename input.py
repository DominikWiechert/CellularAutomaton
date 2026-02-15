import math
from typing import List
from matplotlib import pyplot as plt
from pathlib import Path
import cv2
import numpy as np
from pykrige.ok import OrdinaryKriging

from custom_datatypes import MapNode, LandUse

def get_forest_map(map_path: Path = None, nodes_per_axis: int = 200, axis_length: float = None, heights: list[list[float]] = [[1,1,1]], show_height_graph: bool = False) -> List[List[MapNode]]:
    """
    Return a 2D forest map of a given map picture.
    :param show_height_graph:
    :param axis_length:
    :param map_path:
    :param nodes_per_axis:
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
        n_nodes_width = nodes_per_axis
        n_nodes_height = int(n_nodes_width / ratio)
    else:
        n_nodes_height = nodes_per_axis
        n_nodes_width = int(ratio * n_nodes_height)

    input_image = cv2.resize(input_image,(n_nodes_width, n_nodes_height))
    input_image = cv2.cvtColor(input_image, cv2.COLOR_BGR2Luv)
    forest_color = get_forest_color_luv()
    [l_forest, u_forest, v_forest] = forest_color[0], forest_color[1], forest_color[2]

    cell_size = axis_length / nodes_per_axis
    data_heights_x = np.array([float(dataset[0]) for dataset in heights])
    data_heights_y = np.array([float(dataset[1]) for dataset in heights])
    data_heights = np.array([float(dataset[2]) for dataset in heights])

    # Grid for interpolation
    grid_x = np.arange(0, n_nodes_height*cell_size, 1, dtype=float)
    grid_y = np.arange(0, n_nodes_width*cell_size, 1, dtype=float)

    # Initiate Ordinary Kriging object
    OK = OrdinaryKriging(
        data_heights_x,
        data_heights_y,
        data_heights,
        variogram_model='spherical',
        verbose=False,
        enable_plotting=False
    )
    # Execute interpolation
    interpolated_heights, _ = OK.execute('grid', grid_x, grid_y)

    if show_height_graph:
        plt.figure(figsize=(6, 5))
        # Coordinate system is flipped by 90 degrees (clockwise)
        # x and y values are changed and y-axis is getting inverted.
        plt.contourf(grid_y, grid_x, interpolated_heights, cmap='viridis')
        plt.scatter(data_heights_y, data_heights_x, c=data_heights, edgecolor='k', cmap='viridis')
        plt.colorbar(label='Interpolated Heights [m]')
        plt.title("Interpolated Heights")
        plt.xlabel("y")
        plt.ylabel("x")
        plt.gca().invert_yaxis()
        plt.show()

    output_grid = []
    for i_height in range(input_image.shape[0]):
        row = []
        for i_width in range(input_image.shape[1]):
            position_width = int(i_width * cell_size)
            position_height = int(i_height * cell_size)
            pixel_height = interpolated_heights[position_width][position_height]
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
