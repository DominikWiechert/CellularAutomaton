from typing import List
import random
import yaml
import os.path
from custom_datatypes import MapNode, NodeStatus, Probability, OptimisedCell
import numpy as np


def log(msg):
    DEBUG = True
    if DEBUG == True:
        print(f'\033[92m **',msg,f'**\033[0m')

def calculate_probability():
    wind_v_max = 100
    if os.path.isfile("config.yaml"):
        with open("config.yaml", 'r') as file:
            config = yaml.safe_load(file)
        log("Probability config loaded")
    else:
        config = {
            "probability": 30,
            "wind_speed_x": -80,
            "wind_speed_y": -30
        }
        with open("config.yaml", 'w') as file:
            yaml.dump(config, file,default_flow_style=False)
        log("Probability config not existing")
        log("Standard probability config file created")
    probability = Probability(config["probability"])

    probability.north = probability.base * (1 + config["wind_speed_x"]/wind_v_max)
    probability.south = probability.base * (1 - config["wind_speed_x"]/wind_v_max)
    probability.west = probability.base * (1 + config["wind_speed_y"]/wind_v_max)
    probability.east = probability.base * (1 - config["wind_speed_y"]/wind_v_max)

    log("Probability calculated")
    log("Spread prob. east: " + str(probability.east))
    log("Spread prob. west: " + str(probability.west))
    log("Spread prob. north: " + str(probability.north))
    log("Spread prob. south: " + str(probability.south))

    prob_ground = probability.base*0.6
    return probability,prob_ground

def calc_incl(h_local,h_neighbor,abst):
    abst = 5 #TODO: calculate distance of tiles
    return ((np.arcsin((h_neighbor-h_local)/abst) + 90) / 90)

def run_simulation_step(forest_map: List[List[MapNode]], probability_crown, probability_ground: float, distance: float) -> List[List[MapNode]]:
    forest_map_temp = forest_map.copy()
    for k in range(len(forest_map)):
        for l in range(len(forest_map[0])):
            if forest_map[k][l].status == NodeStatus.CROWN_BURNING:
                if k != 0:
                    if (forest_map[k - 1][l].status == NodeStatus.INTACT or forest_map[k - 1][l].status == NodeStatus.LOWER_BURNING) and random.randint(1, 100*round(calc_incl(forest_map[k ][l].height,forest_map[k - 1][l].height,1))) <= probability_crown.west: #west
                        forest_map_temp[k - 1][l].status = NodeStatus.CROWN_BURNING
                if l != 0:
                    if (forest_map[k][l - 1].status == NodeStatus.INTACT or forest_map[k][l - 1].status == NodeStatus.LOWER_BURNING) and random.randint(1, 100*round(calc_incl(forest_map[k ][l].height,forest_map[k][l-1].height,1))) <= probability_crown.south: #south
                        forest_map_temp[k][l - 1].status = NodeStatus.CROWN_BURNING
                if k != len(forest_map) - 1:
                    if (forest_map[k + 1][l].status == NodeStatus.INTACT or forest_map[k + 1][l].status == NodeStatus.LOWER_BURNING) and random.randint(1, 100*round(calc_incl(forest_map[k ][l].height,forest_map[k + 1][l].height,1))) <= probability_crown.east: #east
                        forest_map_temp[k + 1][l].status = NodeStatus.CROWN_BURNING
                if l != len(forest_map[0]) - 1:
                    if (forest_map[k][l + 1].status == NodeStatus.INTACT or forest_map[k][l + 1].status == NodeStatus.LOWER_BURNING) and random.randint(1, 100*round(calc_incl(forest_map[k ][l].height,forest_map[k][l+1].height,1))) <= probability_crown.north: #north
                        forest_map_temp[k][l + 1].status = NodeStatus.CROWN_BURNING

                #-- Burning down --
                if forest_map[k][l].burning_duration >= 5:
                    forest_map_temp[k][l].status = NodeStatus.BURNT_DOWN
                else:
                    forest_map_temp[k][l].burning_duration += 1
            elif forest_map[k][l].status == NodeStatus.LOWER_BURNING: #Groundfire not effected by wind, only by dryness and elevation
                if k != 0:
                    if forest_map[k - 1][l].status == NodeStatus.INTACT and random.randint(1, 100*round(calc_incl(forest_map[k ][l].height,forest_map[k - 1][l].height,1))) <= probability_ground: #west
                        forest_map_temp[k - 1][l].status = NodeStatus.LOWER_BURNING
                if l != 0:
                    if forest_map[k][l - 1].status == NodeStatus.INTACT and random.randint(1, 100*round(calc_incl(forest_map[k ][l].height,forest_map[k][l-1].height,1))) <= probability_ground: #south
                        forest_map_temp[k][l - 1].status = NodeStatus.LOWER_BURNING
                if k != len(forest_map) - 1:
                    if forest_map[k + 1][l].status == NodeStatus.INTACT and random.randint(1, 100*round(calc_incl(forest_map[k ][l].height,forest_map[k + 1][l].height,1))) <= probability_ground: #east
                        forest_map_temp[k + 1][l].status = NodeStatus.LOWER_BURNING
                if l != len(forest_map[0]) - 1:
                    if forest_map[k][l + 1].status == NodeStatus.INTACT and random.randint(1, 100*round(calc_incl(forest_map[k ][l].height,forest_map[k][l+1].height,1))) <= probability_ground: #north
                        forest_map_temp[k][l + 1].status = NodeStatus.LOWER_BURNING
                if random.randint(1, 50) == 1:
                    forest_map[k][l].status = NodeStatus.CROWN_BURNING
                elif random.randint(1, 50) == 1:
                    forest_map[k][l].status = NodeStatus.INTACT
    return forest_map_temp

def print_map_2_console(forest_map: List[List[MapNode]]) -> None:
    for k in range(len(forest_map)):
        for l in range(len(forest_map[0])):
            print(forest_map[k][l].status)


def simplify_forest_map(forest_map: List[List[MapNode]]) -> List[List[str]]:
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

    return simplified_forest_map

def count_cells(forest_map):
    g_count=0
    r_count=0
    b_count=0
    gr_count=0
    unk_count = 0
    o_count = 0
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
    return np.array([[g_count],[r_count],[b_count],[gr_count],[o_count],[unk_count]])

def optimised_render(map,next_map):
    optimised_rendered = []

    for i in range(len(map)):
        for j in range(len(map[0])):
            if map[i][j] != next_map[i][j]:
                cell = OptimisedCell(next_map[i][j], i,j,map[i][j])
                optimised_rendered.append(cell)
    return optimised_rendered