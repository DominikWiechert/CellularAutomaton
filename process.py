from typing import List
import random
import yaml
import os.path
from custom_datatypes import MapNode, NodeStatus, Probability, OptimisedCell
import numpy as np


def log(msg):
    """
    Set DEBUG == False to supress debugging messages.
    """
    DEBUG = True
    if DEBUG == True:
        print(f'\033[92m **',msg,f'**\033[0m')

def calculate_probability(dryness_factor: float, wind_x: float, wind_y: float):
    """
    Calculates global fire propagation probability for each cardinal direction.
    """
    wind_v_max = 100 #Can be edited to make simulation more precise
    probability = Probability(dryness_factor)
    probability.west = probability.base * (1 + wind_x/wind_v_max)
    probability.east = probability.base * (1 - wind_x/wind_v_max)
    probability.north = probability.base * (1 + wind_y/wind_v_max) #süd
    probability.south = probability.base * (1 - wind_y/wind_v_max) #nord

    log("Probability calculated")
    log("Spread prob. east: " + str(probability.east))
    log("Spread prob. west: " + str(probability.west))
    log("Spread prob. north: " + str(probability.north))
    log("Spread prob. south: " + str(probability.south))

    prob_ground = probability.base*0.6  #The factor 0.6 is based on observation of Wildfires. Can be changed later on to adapt model to real world wildfires.
    return probability, prob_ground

def calc_incl(h_local,h_neighbor,abst):
    """
    Calculates factor based on inline between two Cells. Factor is used to reduce/increase propagation probability.
    """
    incl = np.arctan((h_neighbor-h_local) / abst) *180/np.pi
    return (-incl + 90) / 90 #Returns Number between 2 and 0.

def run_simulation_step(forest_map: List[List[MapNode]], probability_crown, probability_ground: float, distance: float) -> List[List[MapNode]]:
    """
    Calculates the next simulation Step based on the current.
    """
    forest_map_temp = forest_map.copy() #Copies Map to insure parallelism
    for k in range(len(forest_map)):
        for l in range(len(forest_map[0])):
            if forest_map[k][l].status == NodeStatus.CROWN_BURNING: #Checks fire propagation on crown level
                if k != 0:
                    if (forest_map[k - 1][l].status == NodeStatus.INTACT or forest_map[k - 1][l].status == NodeStatus.LOWER_BURNING) and random.randint(1, round(100*calc_incl(forest_map[k][l].height,forest_map[k - 1][l].height,distance))) <= probability_crown.north:
                        forest_map_temp[k - 1][l].status = NodeStatus.CROWN_BURNING
                if l != 0:
                    if (forest_map[k][l - 1].status == NodeStatus.INTACT or forest_map[k][l - 1].status == NodeStatus.LOWER_BURNING) and random.randint(1, round(100*calc_incl(forest_map[k][l].height,forest_map[k][l-1].height,distance))) <= probability_crown.east:
                        forest_map_temp[k][l - 1].status = NodeStatus.CROWN_BURNING
                if k != len(forest_map) - 1:
                    if (forest_map[k + 1][l].status == NodeStatus.INTACT or forest_map[k + 1][l].status == NodeStatus.LOWER_BURNING) and random.randint(1, round(100*calc_incl(forest_map[k][l].height,forest_map[k + 1][l].height,distance))) <= probability_crown.south:
                        forest_map_temp[k + 1][l].status = NodeStatus.CROWN_BURNING
                if l != len(forest_map[0]) - 1:
                    if (forest_map[k][l + 1].status == NodeStatus.INTACT or forest_map[k][l + 1].status == NodeStatus.LOWER_BURNING) and random.randint(1, round(100*calc_incl(forest_map[k][l].height,forest_map[k][l+1].height,distance))) <= probability_crown.west:
                        forest_map_temp[k][l + 1].status = NodeStatus.CROWN_BURNING

                if forest_map[k][l].burning_duration >= 5: #Checks if Cell is burned down
                    forest_map_temp[k][l].status = NodeStatus.BURNT_DOWN
                else:
                    forest_map_temp[k][l].burning_duration += 1
            elif forest_map[k][l].status == NodeStatus.LOWER_BURNING: #Checks propagation of fire on ground level; Propagation is not effected by wind, only by dryness and elevation
                if k != 0:
                    if forest_map[k - 1][l].status == NodeStatus.INTACT and random.randint(1, round(100*calc_incl(forest_map[k][l].height,forest_map[k - 1][l].height,distance))) <= probability_ground: #west
                        forest_map_temp[k - 1][l].status = NodeStatus.LOWER_BURNING
                if l != 0:
                    if forest_map[k][l - 1].status == NodeStatus.INTACT and random.randint(1, round(100*calc_incl(forest_map[k][l].height,forest_map[k][l-1].height,distance))) <= probability_ground: #south
                        forest_map_temp[k][l - 1].status = NodeStatus.LOWER_BURNING
                if k != len(forest_map) - 1:
                    if forest_map[k + 1][l].status == NodeStatus.INTACT and random.randint(1, round(100*calc_incl(forest_map[k][l].height,forest_map[k + 1][l].height,distance))) <= probability_ground: #east
                        forest_map_temp[k + 1][l].status = NodeStatus.LOWER_BURNING
                if l != len(forest_map[0]) - 1:
                    if forest_map[k][l + 1].status == NodeStatus.INTACT and random.randint(1, round(100*calc_incl(forest_map[k][l].height,forest_map[k][l+1].height,distance))) <= probability_ground: #north
                        forest_map_temp[k][l + 1].status = NodeStatus.LOWER_BURNING
                if random.randint(1, 50) == 1: #Checks if fire spreads from ground level to crown
                    forest_map[k][l].status = NodeStatus.CROWN_BURNING
                elif random.randint(1, 50) == 1: #Checks if fire extinguishes on its own
                    forest_map[k][l].status = NodeStatus.INTACT
    return forest_map_temp


def simplify_forest_map(forest_map: List[List[MapNode]]) -> List[List[str]]:
    """
    Translates forest_map with MapNode elements to an array of strings, which indicate color of cell.
    """
    simplified_forest_map  = [["cyan" for x in range(len(forest_map[0]))] for y in range(len(forest_map))] #cyan indicates error
    for i in range(len(forest_map)):
        for j in range(len(forest_map[0])):
            if forest_map[i][j].status == NodeStatus.INTACT:
                simplified_forest_map[i][j] = "green"
            elif forest_map[i][j].status == NodeStatus.CROWN_BURNING:
                simplified_forest_map[i][j] = "red"
            elif forest_map[i][j].status == NodeStatus.BURNT_DOWN:
                simplified_forest_map[i][j] = "black"
            elif forest_map[i][j].status == NodeStatus.CANNOT_BURN:
                simplified_forest_map[i][j] = "grey"
            elif forest_map[i][j].status == NodeStatus.LOWER_BURNING:
                simplified_forest_map[i][j] = "orange"
    return simplified_forest_map #If no error occurred, no cell should be visualised as cyan

def count_cells(forest_map):
    """
    Counts number of cell colors in a forest_map. Returns them in an 2D-Array.
    """
    g_count=0 #Number of green cells
    r_count=0 #Number of red cells
    b_count=0 #Number of black cells
    gr_count=0 #Number of grey cells
    o_count = 0 #Number of orange cells
    unk_count = 0  #Number of cells, which could not be identified
    for i in range(len(forest_map)):
        for j in range(len(forest_map[0])):
            if forest_map[i,j] == b'green':
                g_count += 1
            elif forest_map[i,j] == b'red':
                r_count += 1
            elif forest_map[i,j] == b'black':
                b_count += 1
            elif forest_map[i,j] == b'grey':
                gr_count += 1
            elif forest_map[i,j] == b'orange':
                o_count += 1
            else:
                unk_count += 1
    return np.array([[g_count],[r_count],[b_count],[gr_count],[o_count],[unk_count]]) #If no error occurred, unk_count should be == 0

def optimised_render(map,next_map):
    """
    Compares map and next_map. Any color change of a Cell gets saved in list optimised_rendered.
    """
    optimised_rendered = []
    for i in range(len(map)):
        for j in range(len(map[0])):
            if map[i][j] != next_map[i][j]:
                cell = OptimisedCell(next_map[i][j], i,j,map[i][j])
                optimised_rendered.append(cell)
    return optimised_rendered